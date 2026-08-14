# 🎓 CMU Smart Scheduler (AI-Powered Course Assistant)

**An Intelligent Course Planning and Scheduling System for Chiang Mai University**

This project is a Proof of Concept (PoC) demonstrating an automated curriculum extraction pipeline and an AI-driven Chatbot. The system is designed to assist university students in seamlessly organizing their academic schedules, recommending elective courses, and auditing graduation requirements.

---

## 🛠️ System Architecture

The architecture relies on a **Zero-Shot RAG (Retrieval-Augmented Generation)** methodology to ensure the AI utilizes only official university data, eliminating hallucination in factual recommendations. The system is divided into three core microservices:

1. **Data Engineering Pipeline (Backend):** Automated extraction and optimization of unstructured data (PDFs/Web Scraping) into machine-readable JSON/CSV formats.
2. **AI Logic Engine (Core Brain):** Advanced constraint-solving and scheduling algorithms utilizing LLMs.
3. **Frontend Interface:** A user interaction layer designed for messaging platforms (e.g., LINE Official Account) or standalone Web Applications.

---

## 🧠 Core Technologies & Engineering Challenges

### 1. Data Optimization (Token Limit Management)
*   **Challenge:** Feeding the entire university schedule (initially in massive JSON formats) into the LLM exceeded context window limits (Token Resource Exhaustion).
*   **Solution:** Developed a Python optimization script (`src/pipeline/compress_schedule.py`) to parse, filter, and compress the payload into a highly efficient, pipe-delimited `CSV` format, reducing token usage by nearly 50% and significantly improving response latency.

### 2. Overcoming Mathematical Hallucinations (Chain-of-Thought)
*   **Challenge:** Large Language Models excel at natural language but struggle with combinatorial mathematics (e.g., detecting overlapping time slots across hundreds of course sections).
*   **Solution:** Implemented advanced **Chain-of-Thought (CoT)** prompting. The system strictly forces the AI to execute a step-by-step reasoning process—evaluating time constraints and section availability systematically—before finalizing a collision-free markdown table schedule.

---

## 📂 Repository Structure

*   `raw_data/`: Unprocessed curriculum PDFs, Excel schedules, and raw OCR text extractions.
*   `data/json_db/`: The cleaned, optimized databases (JSON and CSV) serving as the RAG knowledge base.
*   `src/pipeline/`: Python data engineering scripts for PDF extraction, OCR, and JSON/CSV compilation.
*   `src/ocr/`: Scripts for processing image-based conditions utilizing Gemini Vision APIs.
*   `src/bot/`: Core chatbot execution files (`chatbot_ai_demo.py`), featuring the optimized CoT system prompts and user interaction loops.
*   `docs/`: Presentation workflow and system documentation.

---

## 🚀 Future Work (Deployment Roadmap)

To scale this Proof of Concept into a production-grade application for university-wide adoption:

1.  **Matthew Platform Integration:** Deploying the optimized knowledge base and system prompt as a "Custom Bot" on **Matthew (CMU's Generative AI Platform)**, allowing students to securely log in via their CMU IT Accounts.
2.  **Function Calling (Agentic AI):** Upgrading the LLM from relying purely on Chain-of-Thought to utilizing `Python Function Calling`. This will delegate the schedule collision mathematical checks back to Python, guaranteeing 100% computational accuracy for highly complex senior-year schedules.
3.  **Real-Time API Integration:** Transitioning from static CSV databases to real-time API polling against the university registration system to evaluate live seat availability.

---

## 💻 Getting Started

To run the local prototype:
1. Clone this repository.
2. Initialize a virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the core chatbot logic: `python src/bot/chatbot_ai_demo.py`