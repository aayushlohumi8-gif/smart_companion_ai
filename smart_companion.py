import requests
import json
import datetime
import os
import wikipediaapi
import threading

# 👉 Paste your DeepSeek/OpenRouter API key here
API_KEY = "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"

# Wikipedia setup with proper user agent
wiki_wiki = wikipediaapi.Wikipedia(user_agent="smart_companion_ai/1.0", language='en')

def get_wikipedia_summary(query, sentences=2):
    """Fetch a short summary from Wikipedia for factual questions."""
    page = wiki_wiki.page(query)
    if page.exists():
        return ". ".join(page.summary.split(".")[:sentences]) + "."
    return None

def deepseek_response(user_input, messages, result_dict):
    """Fetch response from DeepSeek API."""
    messages.append({"role": "user", "content": user_input})
    data = {"model": "deepseek/deepseek-chat", "messages": messages}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        ai_reply = result["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": ai_reply})
        result_dict["deepseek"] = ai_reply
    except Exception as e:
        result_dict["deepseek"] = f"⚠️ Error contacting DeepSeek API: {e}"

# DeepSeek API setup
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Chat session
messages = [{"role": "system", "content": "You are a helpful AI assistant."}]

# Create folder for chats
if not os.path.exists("chat_history"):
    os.makedirs("chat_history")

# Generate unique filename with timestamp
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
chat_file = os.path.join("chat_history", f"smart_companion_chat_{timestamp}.txt")

print("🤖 Smart Companion AI (type 'exit' to quit)\n")
print(f"📁 Chat will be saved to: {chat_file}\n")

# Factual triggers
factual_triggers = [
    "president of", "prime minister of", "capital of",
    "current president", "current prime minister", "current capital"
]

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Chat ended. Conversation saved in:", chat_file)
        break

    result_dict = {}

    # Check if query is factual
    is_factual = any(trigger in user_input.lower() for trigger in factual_triggers)

    # Start DeepSeek in a separate thread
    deepseek_thread = threading.Thread(target=deepseek_response, args=(user_input, messages, result_dict))
    deepseek_thread.start()

    # Wikipedia query runs in main thread (can also be a thread)
    wiki_answer = get_wikipedia_summary(user_input, sentences=2) if is_factual else None

    # Wait for DeepSeek to finish
    deepseek_thread.join()

    # Decide which answer to use
    if wiki_answer:
        ai_reply = f"(Verified from Wikipedia) {wiki_answer}"
    elif "deepseek" in result_dict:
        ai_reply = result_dict["deepseek"]
    else:
        ai_reply = "⚠️ No response from AI."

    print("AI:", ai_reply, "\n")

    # Save chat
    with open(chat_file, "a", encoding="utf-8") as f:
        f.write(f"You: {user_input}\n")
        f.write(f"AI: {ai_reply}\n\n")
