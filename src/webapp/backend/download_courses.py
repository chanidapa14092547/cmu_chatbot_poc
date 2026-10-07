#!/usr/bin/env python3
"""Download public CMU course offerings without a browser or interactive login."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import math
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from http.client import IncompleteRead
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, Tag


BASE_URL = "https://www1.reg.cmu.ac.th/registrationoffice/searchcourse.php"
LOG = logging.getLogger("cmu_courses")
COURSE_HEADER = re.compile(r"^(\d{6})\s*-\s*\(\s*(\d+)\s+Sections?\s*\)")
SECTION_FIELDS = [
    "course_code", "offering_type", "lecture_section", "lab_section",
    "parent_lecture_section", "parent_lab_section", "status", "title_english",
    "title_thai", "notes", "lecture_credits", "lab_credits", "days_1", "days_2",
    "time_1", "time_2", "room_1", "room_2", "lecturers", "seats", "enrolled",
    "waiting_add", "waiting_move_in", "waiting_move_out", "waiting_drop",
    "condition_text", "condition_url",
]
CSV_FIELDS = ["term", *SECTION_FIELDS, "midterm_exam", "final_exam", "description_url"]


class DownloadError(Exception):
    """A response could not be fetched or safely interpreted."""


def text(node: Tag | None) -> str:
    return " ".join(node.get_text(" ", strip=True).split()) if node else ""


def lines(node: Tag) -> list[str]:
    return [" ".join(part.split()) for part in node.stripped_strings if part.strip()]


def number(node: Tag) -> int | float | None:
    value = text(node).replace(",", "")
    if not value:
        return None  # An undisclosed count is not zero.
    if not re.fullmatch(r"\d+(?:\.\d+)?", value):
        raise DownloadError(f"Unexpected numeric cell: {value!r}")
    return float(value) if "." in value else int(value)


def selected_term(soup: BeautifulSoup) -> tuple[str, list[dict]]:
    select = soup.find("select", attrs={"name": "tterm"})
    if select is None:
        raise DownloadError("Term selector missing; the site may have changed or returned a login/error page.")
    terms = [
        {"value": option["value"], "label": text(option)}
        for option in select.find_all("option") if option.get("value")
    ]
    selected = select.find("option", selected=True)
    if selected is None or not selected.get("value"):
        raise DownloadError("The site did not select a current term; supply a valid term after checking the site.")
    return selected["value"], terms


def resolve_term(requested: str | None, current: str, terms: list[dict]) -> str:
    if requested is None:
        return current
    values = [term["value"] for term in terms]
    if requested in values:
        return requested
    # The site's archived terms carry an H suffix in their form values.
    if requested + "H" in values:
        return requested + "H"
    raise DownloadError(f"Unknown term {requested!r}. Available values: {', '.join(values)}")


def fetch(url: str, data: dict[str, str] | None, timeout: float, attempts: int) -> bytes:
    payload = urlencode(data).encode("ascii") if data is not None else None
    headers = {"User-Agent": "CMUCourseDownloader/1.0 (public course offerings)",
               "Accept": "text/html", "Referer": BASE_URL}
    for attempt in range(attempts):
        try:
            request = Request(url, data=payload, headers=headers)
            with urlopen(request, timeout=timeout) as response:
                if response.headers.get_content_type() != "text/html":
                    raise DownloadError("Expected an HTML course-search response.")
                return response.read()
        except HTTPError as exc:
            exc.close()
            if exc.code not in {429, 500, 502, 503, 504}:
                raise DownloadError(f"HTTP {exc.code} for {url}") from exc
            error = exc
            retry_after = exc.headers.get("Retry-After", "")
            if retry_after and (not retry_after.isdigit() or int(retry_after) > 60):
                raise DownloadError(f"Server asked to retry later ({retry_after}); stopping this run.") from exc
            delay = max(2 ** (attempt + 1), int(retry_after or 0))
        except (URLError, TimeoutError, IncompleteRead, ConnectionError) as exc:
            error = exc
            delay = 2 ** (attempt + 1)
        if attempt + 1 < attempts:
            LOG.warning("Request failed (%s). Retrying in %s seconds.", error, delay)
            time.sleep(delay)
    raise DownloadError(f"Request failed after {attempts} attempts: {error}")


def schedule_pair(cell: Tag) -> tuple[str, str]:
    # Preserve each displayed slot, including an empty first/second slot.
    first = cell.find("div", recursive=False)
    second = cell.find("span", recursive=False)
    if first is None:
        raise DownloadError("Schedule cell layout changed (expected a primary div).")
    return text(first), text(second)


def parse_regular(cells: list[Tag], course_code: str) -> dict:
    title = lines(cells[2])
    if not re.fullmatch(r"\d{3}", text(cells[3])) or not re.fullmatch(r"\d{3}", text(cells[4])):
        raise DownloadError(f"Invalid section cells for {course_code}.")
    record = dict.fromkeys(SECTION_FIELDS, "")
    record.update(
        course_code=course_code, offering_type="regular", status=text(cells[0]),
        title_english=title[0] if title else "", title_thai=title[1] if len(title) > 1 else "",
        notes="\n".join(title[2:]), lecture_section=text(cells[3]), lab_section=text(cells[4]),
        lecture_credits=number(cells[5]), lab_credits=number(cells[6]),
        lecturers="\n".join(lines(cells[10])), condition_text=text(cells[1]),
    )
    condition = cells[1].find("a", href=True)
    record["condition_url"] = urljoin(BASE_URL, condition["href"]) if condition else ""
    for index, name in [(7, "days"), (8, "time"), (9, "room")]:
        record[f"{name}_1"], record[f"{name}_2"] = schedule_pair(cells[index])
    for index, name in enumerate(
        ["seats", "enrolled", "waiting_add", "waiting_move_in", "waiting_move_out", "waiting_drop"], 11
    ):
        record[name] = number(cells[index])
    return record


def parse_lifelong(cells: list[Tag], parent: dict | None) -> dict:
    if parent is None or "CMU Lifelong" not in text(cells[0]):
        raise DownloadError("Unrecognized supplemental section row.")
    if not all(re.fullmatch(r"\d{3}", text(cells[i])) for i in (1, 2)):
        raise DownloadError("Invalid CMU Lifelong section identifier.")
    record = dict.fromkeys(SECTION_FIELDS, "")
    record.update(
        course_code=parent["course_code"], offering_type="lifelong",
        lecture_section=text(cells[1]), lab_section=text(cells[2]),
        parent_lecture_section=parent["lecture_section"], parent_lab_section=parent["lab_section"],
        title_english=parent["title_english"], title_thai=parent["title_thai"],
        notes=text(cells[0]), lecture_credits=number(cells[3]), lab_credits=number(cells[4]),
        lecturers="\n".join(lines(cells[8])), seats=number(cells[9]), enrolled=number(cells[10]),
        waiting_add=number(cells[11]), waiting_move_in=None, waiting_move_out=None, waiting_drop=None,
    )
    # The page leaves these empty for linked offerings; do not invent values.
    for index, name in [(5, "days"), (6, "time"), (7, "room")]:
        if text(cells[index]):
            record[f"{name}_1"] = text(cells[index])
    return record


def parse_results(html: bytes, expected_term: str) -> dict:
    if not re.search(rb"</html>\s*$", html, re.I):
        raise DownloadError("Incomplete HTML response. Raw data saved; no successful export produced.")
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
    actual_term, _ = selected_term(soup)
    if actual_term != expected_term:
        raise DownloadError(f"Requested {expected_term}, but server returned {actual_term}.")
    marker = soup.find("a", attrs={"name": "showrecord"})
    if marker is None:
        raise DownloadError("Search-results marker missing.")
    tables = soup.select("table.tblCourse")
    empty_message = marker.parent.find("h4", string=lambda value: value and value.strip() == "ไม่พบข้อมูล")
    if not tables and empty_message is None:
        raise DownloadError("No course table returned. The search may be empty or the site may have changed.")
    courses, sections = [], []
    current, parent = None, None
    for table in tables:
        for row in table.find_all("tr"):
            if row.find_parent("table") is not table:
                continue
            cells = row.find_all(["th", "td"], recursive=False)
            if not cells:
                continue
            if cells[0].name == "th":
                heading = cells[0].find("div")
                heading_text = text(heading)
                match = COURSE_HEADER.match(heading_text)
                if not match:
                    raise DownloadError(f"Unrecognized course header: {heading_text!r}")
                exams = dict(re.findall(
                    r"(MIDTERM|FINAL)\s+Exam\s*=>\s*(.*?)(?=\s*(?:MIDTERM|FINAL)\s+Exam|$)",
                    heading_text[match.end():],
                ))
                link = cells[0].find("a", href=re.compile(r"coursepublic\.aspx"))
                current = {"course_code": match[1], "section_count": int(match[2]),
                           "midterm_exam": exams.get("MIDTERM", "").strip(),
                           "final_exam": exams.get("FINAL", "").strip(),
                           "description_url": urljoin(BASE_URL, link["href"]) if link else ""}
                courses.append(current)
                parent = None
                continue
            if text(cells[0]) in {"STATUS", "LEC"}:
                continue
            if current is None:
                raise DownloadError("Section encountered before its course header.")
            if len(cells) == 17 and all(c.get("colspan", "1") == "1" for c in cells):
                parent = parse_regular(cells, current["course_code"])
                sections.append(parent)
            elif len(cells) == 12 and cells[0].get("colspan") == "3":
                sections.append(parse_lifelong(cells, parent))
            else:
                raise DownloadError(f"Unrecognized row for {current['course_code']}: {len(cells)} cells.")
    codes = [course["course_code"] for course in courses]
    if len(set(codes)) != len(codes):
        raise DownloadError("Duplicate course headers in the response.")
    counts = Counter(row["course_code"] for row in sections if row["offering_type"] == "regular")
    for course in courses:
        if counts[course["course_code"]] != course["section_count"]:
            raise DownloadError(f"Section count mismatch for {course['course_code']}: "
                                f"expected {course['section_count']}, parsed {counts[course['course_code']]}")
    date_node = soup.find(string=re.compile(r"ข้อมูล ณ วันที่"))
    service = soup.find(string=re.compile(r"000000\s*-\s*ENROLLMENT FOR SERVICE"))
    service_match = re.search(r"Enroll\s*:\s*(\d+)", str(service)) if service else None
    return {
        "source_as_of": " ".join(str(date_node).split()) if date_node else "",
        "enrollment_for_service": {"course_code": "000000", "enrolled": int(service_match[1])}
        if service_match else None,
        "courses": courses, "sections": sections,
    }


def spreadsheet_safe(value):
    # Keep exact source text in JSON; protect CSV consumers from formula execution.
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")) and value != "-":
        return "'" + value
    return value


def export(result: dict, directory: Path) -> None:
    course_lookup = {course["course_code"]: course for course in result["courses"]}
    with (directory / "courses.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for section in result["sections"]:
            course = course_lookup[section["course_code"]]
            row = {"term": result["metadata"]["term"], **section,
                   **{key: course[key] for key in ("midterm_exam", "final_exam", "description_url")}}
            writer.writerow({key: spreadsheet_safe(value) for key, value in row.items()})
    # Written last: a complete JSON document marks a successfully validated export.
    temporary_json = directory / "courses.json.part"
    with temporary_json.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    temporary_json.replace(directory / "courses.json")


def positive_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("must be a finite positive number")
    return parsed


def department_prefix(value: str) -> str:
    if not re.fullmatch(r"[0-9]{3}", value):
        raise argparse.ArgumentTypeError("department must be exactly three digits, e.g. 001 or 204")
    return value


def filter_departments(result: dict, departments: list[str]) -> dict:
    if not departments:
        return result
    prefixes = tuple(departments)
    return {
        **result,
        "courses": [course for course in result["courses"] if course["course_code"].startswith(prefixes)],
        "sections": [section for section in result["sections"] if section["course_code"].startswith(prefixes)],
        "enrollment_for_service": result["enrollment_for_service"] if "000" in departments else None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--term", help="Semester/Buddhist year, e.g. 1/2569; default: site's selected term")
    parser.add_argument("--department", "--dept", type=department_prefix, nargs="+", action="extend",
                        default=[], metavar="PREFIX",
                        help="Only these three-digit course prefixes, e.g. 001 204; can be repeated")
    parser.add_argument("--output-dir", type=Path, default=Path("downloads"), help="Parent output directory")
    parser.add_argument("--timeout", type=positive_float, default=180, help="Request timeout in seconds (default: 180)")
    parser.add_argument("--attempts", type=int, choices=range(1, 6), default=3, help="Maximum request attempts (default: 3)")
    parser.add_argument("--list-terms", action="store_true", help="Print available terms and exit")
    parser.add_argument("--from-html", type=Path, help="Parse a previously saved search.html without any network requests")
    args = parser.parse_args(argv)
    if args.from_html and args.list_terms:
        parser.error("--from-html and --list-terms cannot be combined")
    if args.department and args.list_terms:
        parser.error("--department and --list-terms cannot be combined")
    departments = list(dict.fromkeys(args.department))
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        started = datetime.now(timezone.utc)
        LOG.info("Reading %s", args.from_html or BASE_URL)
        landing = args.from_html.read_bytes() if args.from_html else fetch(BASE_URL, None, args.timeout, args.attempts)
        # All controls precede the result table; avoid parsing the large table twice.
        prefix = landing.split(b'<a name="showrecord">', 1)[0]
        current, terms = selected_term(BeautifulSoup(prefix, "html.parser", from_encoding="utf-8"))
        if args.list_terms:
            for item in terms:
                print(f"{item['value']}\t{item['label']}" + ("\t(current default)" if item["value"] == current else ""))
            return 0
        term = resolve_term(args.term, current, terms)
        scope = ("_department-" + departments[0] if len(departments) == 1
                 else "_departments" if departments else "")
        directory = args.output_dir / (term.replace("/", "-") + scope + "_" + started.strftime("%Y%m%dT%H%M%S_%fZ"))
        directory.mkdir(parents=True, exist_ok=False)
        queries = [(department, {"fgroup": department, "button": "Search"}) for department in departments]
        if not queries:
            queries = [(None, {"ftitle": "%", "button2": "Search"})]
        if args.from_html:
            queries = [(None, None)]
        else:
            (directory / "landing.html").write_bytes(landing)
        result = None
        sources = []
        for index, (department, form) in enumerate(queries):
            if args.from_html:
                raw = landing
            else:
                if index:
                    time.sleep(1)
                LOG.info("Downloading %s for %s...",
                         f"department {department}" if department else "all public courses", term)
                raw = fetch(BASE_URL + "?" + urlencode({"tterm": term}), form, args.timeout, args.attempts)
            filename = "search.html" if len(queries) == 1 else f"search-{department}.html"
            (directory / filename).write_bytes(raw)
            LOG.info("Saved %.1f MB of HTML. Parsing and verifying section counts...", len(raw) / 1_000_000)
            parsed = parse_results(raw, term)
            if department and any(not course["course_code"].startswith(department) for course in parsed["courses"]):
                raise DownloadError(f"Server returned courses outside department {department}.")
            sources.append({"file": filename, "search_form": form,
                            "html_sha256": hashlib.sha256(raw).hexdigest(), "source_as_of": parsed["source_as_of"]})
            if result is None:
                result = parsed
            else:
                result["courses"].extend(parsed["courses"])
                result["sections"].extend(parsed["sections"])
        result = filter_departments(result, departments)
        counts = Counter(row["offering_type"] for row in result["sections"])
        result["metadata"] = {
            "source_url": BASE_URL, "term": term, "term_selection": "explicit" if args.term else "site_default",
            "department_prefixes": departments,
            "run_started_at_utc": started.isoformat(), "exported_at_utc": datetime.now(timezone.utc).isoformat(),
            "input_html": str(args.from_html.resolve()) if args.from_html else None,
            "search_form": sources[0]["search_form"] if len(sources) == 1 else None,
            "html_sha256": sources[0]["html_sha256"] if len(sources) == 1 else None,
            "sources": sources, "course_count": len(result["courses"]),
            "regular_section_count": counts["regular"], "lifelong_section_count": counts["lifelong"],
            "total_section_rows": len(result["sections"]), "section_counts_verified": True,
        }
        export(result, directory)
        LOG.info("Done: %s courses, %s regular sections, %s Lifelong sections.",
                 len(result["courses"]), counts["regular"], counts["lifelong"])
        print(directory.resolve())
        return 0
    except (DownloadError, OSError, ValueError) as exc:
        LOG.error("%s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
