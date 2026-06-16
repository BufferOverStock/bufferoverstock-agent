from security_agent import run_agent

print("Starting test execution of BufferOverStock Agent...")
prompt = "Analyze the scan file at mock_scan.txt and write the security report to security_report.md"
result = run_agent(prompt)
print("\n=== AGENT RESPONSE ===")
print(result)
