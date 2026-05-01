from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import time
from datetime import datetime
import os

app = Flask(__name__)

# 🔑 Multiple API Keys (⚠️ replace with NEW ones, don't expose publicly)
API_KEYS = [
    
]

current_key_index = 0

def configure_api():
    genai.configure(api_key=API_KEYS[current_key_index])

def switch_api():
    global current_key_index
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    print(f"🔄 Switching to API key #{current_key_index + 1}")
    configure_api()

# 📝 System Instruction
homework_tutor_instructions = (
    "You are a helpful and encouraging Homework Solving Assistant. "
    "Your goal is to help students understand concepts, not just give raw answers. "
    "Guidelines: "
    "1. If a user asks a homework question, explain the steps to reach the solution. "
    "2. If the user asks something completely unrelated to education or homework "
    "(like video games, celebrity gossip, or jokes), politely redirect them to "
    "focus on their studies. "
    "3. Use Markdown to format math equations and lists for clarity. "
    "4. Keep the tone supportive and academic."
)

# 🔧 Setup
configure_api()

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=homework_tutor_instructions
)

chat = model.start_chat()

# 📂 Create chat folder
os.makedirs("chats", exist_ok=True)

# 🆕 Create file for this session
filename = f"chats/chat_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
chat_file = open(filename, "w", encoding="utf-8", buffering=1)

print(f"💾 Saving chats to: {filename}")

# 🌐 Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat_api():
    user_input = request.json["message"]

    # Save user message
    chat_file.write(f"You: {user_input}\n")

    # Try APIs
    for attempt in range(len(API_KEYS)):
        try:
            response = chat.send_message(user_input)
            bot_reply = response.text

            # Save bot reply
            chat_file.write(f"Bot: {bot_reply}\n\n")

            return jsonify({"reply": bot_reply})

        except Exception as e:
            print("⚠️ Error:", e)
            switch_api()
            time.sleep(1)

    # If all keys fail
    chat_file.write("Bot: ERROR - All API keys failed\n\n")
    return jsonify({"reply": "All API keys failed. Try later."})

# 🔚 Run server
if __name__ == "__main__":
    app.run(debug=True)
