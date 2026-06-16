import os
from datetime import datetime

KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), "../knowledge/base.txt")


def query_knowledge(query: str) -> str:
    """
    Search the local knowledge base for lines relevant to the query.
    """
    path = os.path.abspath(KNOWLEDGE_PATH)

    if not os.path.exists(path):
        return "Knowledge base not found. Add content to knowledge/base.txt."

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            return "Knowledge base is empty."

        keywords = query.lower().split()
        matches = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            line_lower = line.lower()
            if any(kw in line_lower for kw in keywords):
                matches.append(line)

        if not matches:
            return f"No results found in knowledge base for '{query}'."

        return "\n".join(matches[:10])

    except Exception as e:
        return f"Knowledge base error: {str(e)}"


def save_to_knowledge(topic: str, summary: str) -> str:
    """
    Save a new learned fact to the knowledge base.
    Called automatically by the agent after a successful web search.
    """
    path = os.path.abspath(KNOWLEDGE_PATH)

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d")
        entry = f"\n# Learned {timestamp}: {topic}\n{summary.strip()}\n"

        with open(path, "a", encoding="utf-8") as f:
            f.write(entry)

        return f"Saved to knowledge base: '{topic}'"

    except Exception as e:
        return f"Failed to save to knowledge base: {str(e)}"