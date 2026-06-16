# BufferOverStock Agent

A lightweight agentic AI loop built on the Groq API with Llama 3. The agent reasons step-by-step and calls tools autonomously until it can fully answer a query.

---

## What it does

The agent runs a loop: it sends a user message to an LLM, and if the model decides it needs more information, it calls one of the available tools and feeds the result back in — repeating until it has a final answer.

```
User input
    ↓
LLM (Llama 3 via Groq)
    ↓ tool_call?
  Yes → dispatch tool → result back to LLM → repeat
  No  → return final answer
```

## Tools

| Tool | Description |
|------|-------------|
| `web_search` | DuckDuckGo instant answers — no API key needed |
| `read_file` | Reads any local file into context |
| `write_file` | Creates or overwrites a local file |
| `run_shell` | Executes shell commands with basic safety guardrails |
| `query_knowledge` | Keyword search over a local knowledge base |
| `generate_security_report` | Parses raw security scan logs (Nmap, WPScan, etc.) and outputs a structured Markdown assessment report |

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/BufferOverStock/bufferoverstock-agent.git
cd bufferoverstock-agent
```

**2. Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your Groq API key**
```bash
cp .env.example .env
# open .env and paste your key from console.groq.com
```

**5. Run the agents**
* To run the general-purpose assistant:
  ```bash
  python agent.py
  ```
* To run the dedicated security scanner and report generator:
  ```bash
  python security_agent.py
  ```

---

## Example

**General Query Example:**
```
You: What is SQL injection?

[Agent] Calling tool: query_knowledge({'query': 'SQL injection'})
[Agent] Tool result: SQL injection occurs when user input is not sanitized...

Agent: SQL injection is a vulnerability where unsanitized user input is
passed directly to a database query, allowing an attacker to manipulate
the query logic...
```

**Security Auditing Example:**
```
You: Analyze the scan file at mock_scan.txt and save it to report.md

[Agent] Calling tool: generate_security_report({'scan_file_path': 'mock_scan.txt', 'output_report_path': 'report.md'})
[Agent] Tool result: Successfully generated security report and saved it to 'report.md'. 
Findings Summary: Found 1 Critical (WordPress Version Vulnerability), 1 High...

Agent: The security report has been successfully generated and saved to 'report.md'. The report details a Critical WordPress Core vulnerability, an unauthenticated arbitrary file upload issue in Contact Form 7, and enabled directory browsing.
```

---

## Extending it

**Add a new tool:**
1. Create a function in `tools/`
2. Add its definition to the `TOOLS` list in `agent.py`
3. Add a dispatch case in the `dispatch()` function

**Expand the knowledge base:**
Add plain text entries to `knowledge/base.txt` — one fact per line works best.

---

## Stack

- [Groq API](https://console.groq.com) — fast cloud inference
- Llama 3 70B — reasoning model
- Python stdlib only (no heavy dependencies)

---

## Author

[BufferOverStock](https://github.com/BufferOverStock) — cybersecurity student & AI tooling enthusiast
