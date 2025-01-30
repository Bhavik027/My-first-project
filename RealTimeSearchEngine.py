from googlesearch import search
from groq import Groq
import json
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

SYSTEM_PROMPT = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

CHAT_LOG_FILE = r"Data\ChatLog.json"

def load_chat_log():
    try:
        with open(CHAT_LOG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_chat_log(messages):
    with open(CHAT_LOG_FILE, "w") as f:
        json.dump(messages, f, indent=4)

def google_search(query):
    results = list(search(query, advanced=True, num_results=5))  # Reduced results for efficiency
    answer = f"Search results for '{query}':\n[start]\n"
    for i in results:
        answer += f"Title: {i.title}\nDescription: {i.description}\nURL: {i.url}\n\n" #Added URL

    answer += "[end]"
    return answer

def get_current_information():
    now = datetime.datetime.now()
    return f"Current Time: {now.strftime('%A, %d %B %Y, %H:%M:%S')}"

def realtime_search_engine(prompt):
    messages = load_chat_log()

    messages.append({"role": "user", "content": prompt})

    search_results = google_search(prompt)

    messages.append({"role": "system", "content": search_results})
    messages.append({"role": "system", "content": get_current_information()})
    conversation = [{"role": "system", "content": SYSTEM_PROMPT}] + messages #To structure the conversation

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=conversation,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )

    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content

    answer = answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": answer})
    save_chat_log(messages)
    return answer

if __name__ == "__main__":
    while True:
        prompt = input("\nEnter your query (or type 'exit'): ")
        if prompt.lower() == "exit":
            break
        try:
            response = realtime_search_engine(prompt)
            print(response)
        except Exception as e:
            print(f"An error occurred: {e}")