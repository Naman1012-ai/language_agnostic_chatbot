import json
import re
import urllib.request
import streamlit as st
from deep_translator import GoogleTranslator

# -------------------------------------------------------------------
# Page Setup & Styling
# -------------------------------------------------------------------
st.set_page_config(page_title="Language Agnostic Chatbot", page_icon="🤖")
st.title("🤖 Multi-Feature Language Agnostic Chatbot")
st.caption("Built with Python | Supports Translation, Math, Dictionary, and Export")

# -------------------------------------------------------------------
# Helper Functions (Translation & Features)
# -------------------------------------------------------------------
def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception:
        return text

def translate_from_english(text, target_lang):
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text, target_lang)
    except Exception:
        return text

def evaluate_math(expression):
    clean_expr = re.sub(r'[^0-9\+\-\*\/\(\)\.\s]', '', expression)
    if not clean_expr.strip():
        return None
    try:
        result = eval(clean_expr)
        return f"The result of {clean_expr.strip()} is {result}."
    except Exception:
        return None

def fetch_definition(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            meaning = data[0]['meanings'][0]['definitions'][0]['definition']
            return f"Definition of '{word}': {meaning}"
    except Exception:
        return f"Sorry, I couldn't find a definition for '{word}'."

# -------------------------------------------------------------------
# Knowledge Base & Intent Matching
# -------------------------------------------------------------------
KNOWLEDGE_BASE = {
    "greeting": {
        "keywords": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"],
        "response": "Hello! I am your AI assistant. How can I help you today?"
    },
    "identity": {
        "keywords": ["who are you", "your name", "what are you"],
        "response": "I am a multi-featured, language-agnostic chatbot built with Python!"
    },
    "capabilities": {
        "keywords": ["what can you do", "features", "help", "options"],
        "response": "I can chat in multiple languages, solve math expressions, look up word definitions, and export our conversation!"
    },
    "farewell": {
        "keywords": ["bye", "goodbye", "see you", "exit"],
        "response": "Goodbye! Have a fantastic day ahead!"
    }
}

def process_intent(english_text):
    text_lower = english_text.lower()

    if "define" in text_lower or "meaning of" in text_lower:
        words = text_lower.split()
        return fetch_definition(words[-1])

    if any(char in text_lower for char in ['+', '-', '*', '/']) and any(c.isdigit() for c in text_lower):
        math_result = evaluate_math(text_lower)
        if math_result:
            return math_result

    for intent, data in KNOWLEDGE_BASE.items():
        for keyword in data["keywords"]:
            if keyword in text_lower:
                return data["response"]

    return "I am not sure I completely understand that, but I am learning every day!"

# -------------------------------------------------------------------
# Session State Initialization (Chat Memory)
# -------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar Controls
st.sidebar.header("Chatbot Settings")
language_options = {
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Chinese (Simplified)": "zh-cn",
    "Japanese": "ja",
    "English": "en"
}
selected_language_name = st.sidebar.selectbox("Preferred Output Language:", list(language_options.keys()))
target_lang_code = language_options[selected_language_name]

# Clear Chat Option
if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

# -------------------------------------------------------------------
# Chat Interface Logic
# -------------------------------------------------------------------
# Render past message history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Box
if user_input := st.chat_input("Type your message here..."):
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Process Bot Response
    english_input = translate_to_english(user_input)
    english_reply = process_intent(english_input)
    final_reply = translate_from_english(english_reply, target_lang_code)

    # 3. Show bot message
    st.session_state.messages.append({"role": "assistant", "content": final_reply})
    with st.chat_message("assistant"):
        st.markdown(final_reply)