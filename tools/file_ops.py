import os


def read_file(path: str) -> str:
    """Read and return the contents of a file."""
    path = os.path.expanduser(path)

    if not os.path.exists(path):
        return f"Error: file '{path}' does not exist."

    if os.path.getsize(path) > 1_000_000:  # 1MB limit
        return "Error: file too large to read (>1MB)."

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content if content else "(file is empty)"
    except UnicodeDecodeError:
        return "Error: file appears to be binary, not readable as text."
    except Exception as e:
        return f"Read error: {str(e)}"


def write_file(path: str, content: str) -> str:
    """Write content to a file, creating directories if needed."""
    path = os.path.expanduser(path)

    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{path}'."
    except Exception as e:
        return f"Write error: {str(e)}"
