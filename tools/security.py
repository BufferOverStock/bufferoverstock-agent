import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def generate_security_report(scan_file_path: str, output_report_path: str) -> str:
    """
    Reads a raw security scan file (Nmap, WPScan, Nessus, etc.),
    analyzes it using Groq LLM, and writes a professional Markdown
    security report to the output path.
    """
    scan_file_path = os.path.expanduser(scan_file_path)
    output_report_path = os.path.expanduser(output_report_path)

    if not os.path.exists(scan_file_path):
        return f"Error: Scan file '{scan_file_path}' does not exist."

    try:
        with open(scan_file_path, "r", encoding="utf-8", errors="ignore") as f:
            scan_content = f.read()
    except Exception as e:
        return f"Error reading scan file: {str(e)}"

    if not scan_content.strip():
        return "Error: Scan file is empty."

    # Truncate if extremely large to fit inside context window (e.g. 50k chars max)
    if len(scan_content) > 50000:
        scan_content = scan_content[:50000] + "\n... [Scan Output Truncated for Length] ..."

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY not found in environment variables."

    try:
        client = Groq(api_key=api_key)
        
        # System prompt instructing the LLM on how to parse and format the report
        system_prompt = (
            "You are a Senior Security Consultant and Penetration Tester.\n"
            "Your task is to analyze the provided raw security scan output (e.g., from Nmap, WPScan, Nikto, Nessus, etc.) "
            "and generate a professional, client-ready Security Assessment Report in Markdown format.\n\n"
            "The report MUST follow this structure:\n"
            "# SECURITY ASSESSMENT REPORT\n"
            "**Target:** [Identify target URL or IP from scan]\n"
            "**Date:** [Current Date]\n"
            "**Auditor:** BufferOverStock Security Agent\n\n"
            "## 1. Executive Summary\n"
            "- A brief description of the scan target, tools used, and the overall security status.\n"
            "- A clear risk rating (CRITICAL, HIGH, MEDIUM, LOW) based on the findings.\n\n"
            "## 2. Findings Summary Table\n"
            "| Severity | Finding Name | Affected Port/Service/Component | CVE/ID |\n"
            "|---|---|---|---|\n\n"
            "## 3. Detailed Findings\n"
            "For each finding, include:\n"
            "### [Severity] Finding Name\n"
            "- **Description**: What is the issue?\n"
            "- **Impact**: What could an attacker do?\n"
            "- **Remediation**: Specific, actionable steps to fix or mitigate the vulnerability.\n\n"
            "## 4. Hardening Recommendations\n"
            "- 3-4 general security best practices for the client to improve their security posture.\n\n"
            "Be precise, professional, and technical. Do not invent details; only report what can be reasonably inferred from the logs."
        )

        user_content = f"Here is the raw scan output to analyze:\n\n```text\n{scan_content}\n```"

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.2,
            max_tokens=4096
        )

        report_markdown = response.choices[0].message.content

        # Create output directory if it doesn't exist
        if os.path.dirname(output_report_path):
            os.makedirs(os.path.dirname(os.path.abspath(output_report_path)), exist_ok=True)
            
        with open(output_report_path, "w", encoding="utf-8") as f:
            f.write(report_markdown)

        # Call Groq one more time to get a short bulleted summary for the console output
        summary_prompt = (
            "Based on the security report generated, provide an extremely brief 2-3 line summary of findings "
            "counting the number of Critical, High, Medium, and Low findings found (e.g. 'Found 1 Critical (vsftpd backdoor), 2 High...')."
        )
        summary_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": f"Report:\n{report_markdown}\n\n{summary_prompt}"}
            ],
            temperature=0.1,
            max_tokens=200
        )
        brief_summary = summary_response.choices[0].message.content.strip()

        return (
            f"Successfully generated security report and saved it to '{output_report_path}'.\n"
            f"Findings Summary:\n{brief_summary}"
        )

    except Exception as e:
        return f"Error generating security report: {str(e)}"
