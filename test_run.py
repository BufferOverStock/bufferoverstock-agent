import json
from groq.types.chat.chat_completion_message import ChatCompletionMessage
from groq.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall
from groq.types.chat.chat_completion_message_tool_call import Function

msg = ChatCompletionMessage(
    role="assistant",
    content=None,
    tool_calls=[
        ChatCompletionMessageToolCall(
            id="call_123",
            type="function",
            function=Function(name="web_search", arguments='{"query": "test"}')
        )
    ]
)

messages = [{"role": "user", "content": "hello"}]
messages.append(msg)
messages.append({"role": "tool", "tool_call_id": "call_123", "content": "result"})

print("OK so far")
