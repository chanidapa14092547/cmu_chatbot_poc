from bs4 import BeautifulSoup
import sys

def parse_file(filepath):
    print(f"--- Parsing {filepath} ---")
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    table = soup.find('table')
    if not table:
        print("No table found")
        return
        
    rows = table.find_all('tr')
    for i, row in enumerate(rows[:6]):
        cols = [td.get_text(strip=True).replace('\n', ' ').replace('\r', '') for td in row.find_all(['td', 'th'])]
        print(f"Row {i}: {cols}")

parse_file('DS/229123.xls')
parse_file('DS/229223.xls')
