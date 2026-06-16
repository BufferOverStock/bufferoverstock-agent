import subprocess
import shlex


# Commands that are too dangerous to allow
BLOCKED = [
    "rm -rf", "rm -r /", "mkfs", "dd if=",
    "shutdown", "reboot", "halt", "poweroff",
    "> /dev/sda", "chmod 777 /", "chown -R"
]


def run_shell(command: str) -> str:
    """
    Run a shell command and return stdout + stderr.
    Has basic guardrails against destructive commands.
    """
    # Safety check
    for blocked in BLOCKED:
        if blocked in command:
            return f"Blocked: '{blocked}' is not allowed for safety reasons."

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )

        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += f"\nSTDERR: {result.stderr}"
        if result.returncode != 0:
            output += f"\nExit code: {result.returncode}"

        return output.strip() if output.strip() else "(command ran with no output)"

    except subprocess.TimeoutExpired:
        return "Error: command timed out after 30 seconds."
    except Exception as e:
        return f"Shell error: {str(e)}"
