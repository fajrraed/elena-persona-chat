import json
import os
from groq import Groq

# 1. Place your API key here.
# (Make sure to generate a new key from console.groq.com if you encounter a 401 error)
GROQ_API_KEY = "your ap key here"

# Initialize the Groq client
client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are "Elena", an affectionate, confident, and playful older woman in her late 30s/early 40s. 
The user has a clear crush on you, and you enjoy teasing them gently, caring for them, and giving them attention.

Persona Traits:
- Tone: Warm, confident, flirty, protective, and teasing.
- Dynamic: You act as a charming older figure who enjoys the user's admiration while keeping conversations engaging and playful.
- Memory & Choices: Pay close attention to what the user shares (their name, likes/dislikes, choices, and romantic hints). Frequently reference past conversations and choices to show you care and remember.
"""

MEMORY_FILE = "mommy_memory.json"
MAX_HISTORY_LENGTH = 20  # To prevent the memory file from growing too large and slowing down execution

# Default memory structure
user_memory = {
    "user_nickname": "",
    "saved_choices": [],
    "chat_history": []
}

# Safely load existing memory if it exists
if os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file_handle:
            user_memory = json.load(file_handle)
    except Exception:
        pass


def save_memory():
    """Saves conversations to the JSON file while enforcing the maximum history limit."""
    if "chat_history" in user_memory and len(user_memory["chat_history"]) > MAX_HISTORY_LENGTH:
        user_memory["chat_history"] = user_memory["chat_history"][-MAX_HISTORY_LENGTH:]

    with open(MEMORY_FILE, "w", encoding="utf-8") as file_handle:
        json.dump(user_memory, file_handle, indent=4, ensure_ascii=False)


def generate_dynamic_prompt() -> str:
    """Injects user choices and preferences directly into Elena's primary system prompt."""
    choices = user_memory.get("saved_choices", [])
    memory_context = ""
    if choices:
        memory_context = "\nKey choices and facts you know about the user:\n" + "\n".join(f"- {c}" for c in choices)

    return SYSTEM_PROMPT + memory_context


def chat_with_elena(user_input: str) -> str:
    """Sends the current chat session to Groq utilizing fallback model architecture."""
    formatted_messages = [
        {"role": "system", "content": generate_dynamic_prompt()}
    ]

    # Fetch only the last 10 messages for the API call to keep response times fast
    recent_history = user_memory.get("chat_history", [])[-10:]
    for msg in recent_history:
        formatted_messages.append({"role": msg["role"], "content": msg["content"]})

    formatted_messages.append({"role": "user", "content": user_input})

    # Try connecting using the primary fast model (openai/gpt-oss-20b)
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=formatted_messages,
            temperature=0.8
        )
        ai_reply = response.choices[0].message.content or ""
    except Exception:
        # Fallback to the larger model if the primary model fails or is offline (openai/gpt-oss-120b)
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=formatted_messages,
                temperature=0.8
            )
            ai_reply = response.choices[0].message.content or ""
        except Exception as inner_e:
            return f"[An error occurred while communicating with the service: {inner_e}]"

    # Save inputs and outputs to local JSON memory
    if "chat_history" not in user_memory:
        user_memory["chat_history"] = []

    user_memory["chat_history"].append({"role": "user", "content": user_input})
    user_memory["chat_history"].append({"role": "assistant", "content": ai_reply})
    save_memory()

    return ai_reply


if __name__ == "__main__":
    print("Elena initialized! Type 'quit' or 'exit' to log off.\n")
    while True:
        user_msg = input("You: ")
        if user_msg.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break
        if not user_msg.strip():
            continue
        reply = chat_with_elena(user_msg)
        print(f"\nElena: {reply}\n")
