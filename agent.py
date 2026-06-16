import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
from tools.web_search import web_search
from tools.file_ops import read_file, write_file
from tools.shell import run_shell
from tools.knowledge import query_knowledge, save_to_knowledge

# ── config ──────────────────────────────────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL  = "llama-3.1-8b-instant"

# ── tool definitions (sent to the model) ────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information on a topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a local file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or relative file path."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or overwrite a local file with given content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path":    {"type": "string", "description": "File path to write to."},
                    "content": {"type": "string", "description": "Content to write."}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Run a shell command and return its output. Use carefully.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The shell command to run."}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_knowledge",
            "description": "Search the local knowledge base for relevant information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to look up in the knowledge base."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_to_knowledge",
            "description": "Save a newly learned fact to the local knowledge base for future use. Call this after every successful web search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic":   {"type": "string", "description": "Short title for what was learned, 5 words max."},
                    "summary": {"type": "string", "description": "Clean 2-3 sentence summary of the key facts."}
                },
                "required": ["topic", "summary"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a helpful AI agent with access to tools.

When answering, follow this exact process:
1. ALWAYS check query_knowledge first before anything else.
2. If the knowledge base has a good answer, use it directly.
3. If not, use web_search to find the answer.
4. After a successful web_search, you MUST call save_to_knowledge with:
   - topic: a short title for what was learned (5 words max)
   - summary: a clean 2-3 sentence summary of the key facts
5. Then give the user a clear, well-explained final answer.

Never skip step 4 after a web search. Learning from every query makes you smarter."""

# ── tool dispatcher ──────────────────────────────────────────────────────────
def dispatch(tool_name: str, args: dict) -> str:
    """Call the right tool function and return a string result."""
    try:
        if tool_name == "web_search":
            return web_search(args["query"])
        elif tool_name == "read_file":
            return read_file(args["path"])
        elif tool_name == "write_file":
            return write_file(args["path"], args["content"])
        elif tool_name == "run_shell":
            return run_shell(args["command"])
        elif tool_name == "query_knowledge":
            return query_knowledge(args["query"])
        elif tool_name == "save_to_knowledge":
            return save_to_knowledge(args["topic"], args["summary"])
        else:
            return f"Error: unknown tool '{tool_name}'"
    except Exception as e:
        return f"Tool error: {str(e)}"

# ── agent loop ───────────────────────────────────────────────────────────────
def run_agent(user_input: str) -> str:
    """
    Core agentic loop:
    1. Send user message to model
    2. If model calls a tool → dispatch it, feed result back
    3. Repeat until model returns a plain text response
    """
    messages = [
        {"role": "system",  "content": SYSTEM_PROMPT},
        {"role": "user",    "content": user_input}
    ]

    print(f"\n[Agent] Received: {user_input}")

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=4096
        )

        message = response.choices[0].message

        # No tool calls → model is done, return the answer
        if not message.tool_calls:
            return message.content
        
        # Keep history lean — avoid token limits
        if len(messages) > 10:
            new_messages = [messages[0]] + messages[-9:]
            # Ensure we don't orphan a tool message without its assistant caller
            while len(new_messages) > 1 and new_messages[1].get("role") == "tool":
                new_messages.pop(1)
            messages = new_messages

        # Process every tool call the model requested
        msg_dict = {"role": "assistant", "content": message.content}
        if message.tool_calls:
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        messages.append(msg_dict)

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args_str = tool_call.function.arguments
            args = json.loads(args_str) if args_str else {}

            print(f"[Agent] Calling tool: {name}({args})")
            result = dispatch(name, args)
            print(f"[Agent] Tool result: {result[:200]}...")  # truncate long output

            messages.append({
                "role":         "tool",
                "tool_call_id": tool_call.id,
                "content":      result
            })

# ── CLI entry point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== BufferOverStock Agent ===")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input:
            continue

        answer = run_agent(user_input)
        print(f"\nAgent: {answer}\n")
