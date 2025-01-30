from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os  # Import os for path manipulation

# Use os.path to create platform-independent paths
DATA_DIR = "Data"
CHAT_LOG_PATH = os.path.join(DATA_DIR, "ChatLog.json")

# Ensure the Data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("GroqAPIKey not found in .env file")

client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": System}]

try:
    with open(CHAT_LOG_PATH, "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(CHAT_LOG_PATH, "w") as f:
        dump([], f, indent=4)  # Add indent for readability
        
# Function to get real-time date and time information.
def RealtimeInformation():
    current_date_time = datetime.datetime.now()  # Get the current date and time.
    day = current_date_time.strftime("%A")  # Day of the week.
    date = current_date_time.strftime("%d")  # Day of the month.
    month = current_date_time.strftime("%B")  # Full month name.
    year = current_date_time.strftime("%Y")  # Year.
    hour = current_date_time.strftime("%H")  # Hour in 24-hour format.
    minute = current_date_time.strftime("%M")  # Minute.
    second = current_date_time.strftime("%S")  # Second.
    
    # Format the information into a string.
    data = f"Please use the real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes : {second} seconds.\n"
    return data

# Function to modify the chatbot's response for better formatting.
def AnswerModifier(Answer):
    lines = Answer.split('\n')  # Split the response into lines.
    non_empty_lines = [line for line in lines if line.strip()]  # Remove empty lines.
    modified_answer = '\n'.join(non_empty_lines) # Join the cleaned line back together.
    return modified_answer

# Main chatbot function to handle user queries.
def ChatBot(Query):
    try:
        with open(CHAT_LOG_PATH, "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": Query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")

        messages.append({"role": "assistant", "content": Answer})

        with open(CHAT_LOG_PATH, "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        # DO NOT RECURSIVELY CALL ChatBot(Query) HERE!
        # Instead, handle the error appropriately.
        # Option 1: Clear the chat log and inform the user
        messages = []
        with open(CHAT_LOG_PATH, "w") as f:
            dump(messages, f, indent=4)
        return "An error occurred. The chat log has been reset. Please try again."
        # Option 2: Re-raise the exception if you want to handle it higher up
        # raise  # Re-raise the exception

if __name__ == "__main__":
    while True:
        user_input = input("\nEnter Your Question (or type 'exit'): ")
        if user_input.lower() == 'exit':
            break # Exit the loop if the user types 'exit'
        print(ChatBot(user_input))