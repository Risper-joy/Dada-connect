from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# API Key setup for Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Define the empathy prompt for the Generative AI model
empathy_prompt = """You are an empathetic support assistant for disabled victims of violence. 
When responding to queries, provide supportive advice, suggest practical steps based on documented recommendations, 
and, where relevant, offer information about helplines or resources that victims can reach out to."""

# List of feminine animal names for anonymous chat
animal_names = [
    "Ladybug", "Doe", "Kitten", "Lioness", "Vixen", "Dove", "Hen", "Mermaid", "Swan", "Bunny"
]

# In-memory storage for chat messages
chat_history = []

# Function to generate a unique anonymous animal name
def generate_animal_name():
    name = random.choice(animal_names)
    while any(chat['name'] == name for chat in chat_history):
        name = random.choice(animal_names)
    return name

# Function for empathy-based question answering
def question_answering(question):
    full_prompt = f"{empathy_prompt}\n\nUser: {question}"
    response = model.generate_content([full_prompt])
    return response.text if response and hasattr(response, 'text') else "I'm here to help, but I'm currently unable to provide a response."

# Function for translation using Generative AI
def translation(text, target_language="French"):
    translation_prompt = f"Translate the following text to {target_language}: {text}"
    response = model.generate_content([translation_prompt])
    return response.text if response and hasattr(response, 'text') else "Translation failed."

# Route for the landing page
@app.route('/')
def landing():
    return render_template('landing.html')

# Route for the chat feature with anonymous names
@app.route('/community')
def chat_page():
    if 'code_name' not in session:
        session['code_name'] = generate_animal_name()
    return render_template('community.html', chat_history=chat_history, current_user=session['code_name'])

# Route to handle sending chat messages
@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form.get('message')
    if message:
        chat_history.append({
            'name': session['code_name'], 
            'message': message,
            'is_current_user': True
        })
    return redirect(url_for('chat_page'))

# Route for the AI-powered support and translation feature
@app.route('/forum')
def ai_home():
    return render_template('index2.html')

# Route for AI chat and translation API
@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    text = data.get('text')

    # Check if the input is a translation request
    if text.lower().startswith("translate to"):
        parts = text.split(' ', 3)
        target_language = parts[2] if len(parts) > 2 else "French"
        text_to_translate = parts[3] if len(parts) > 3 else ""
        response = translation(text_to_translate, target_language)
    else:
        response = question_answering(text)

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
