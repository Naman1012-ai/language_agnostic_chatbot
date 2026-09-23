import json
import re
import urllib.request
import streamlit as st
from deep_translator import GoogleTranslator

# -------------------------------------------------------------------
# Page Setup
# -------------------------------------------------------------------
st.set_page_config(page_title="Language Agnostic Chatbot", page_icon="🤖")
st.title("🤖 Multi-Feature Language Agnostic Chatbot")
st.caption("Built with Python | Supports Translation, Math, Dictionary, and Export")

# -------------------------------------------------------------------
# Fixed Helper Functions
# -------------------------------------------------------------------
def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as e:
        return text

def translate_from_english(text, target_lang):
    try:
        # Fixed the bug here: removed extra target_lang parameter
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception as e:
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
# Expanded Knowledge Base
# -------------------------------------------------------------------
KNOWLEDGE_BASE = {
    "greeting": {
        "keywords": ["hello", "hi", "hey", "hlo", "hlw", "greetings", "good morning", "good afternoon", "ssup", "sup"],
        "response": "Hello! I am your assistant. How can I help you today?"
    },
    "status": {
        "keywords": ["how are you", "how r u", "how do you do", "how is it going", "how are u"],
        "response": "I am doing great, thank you for asking! How are you doing?"
    },
    "identity": {
        "keywords": ["who are you", "your name", "what are you", "who made you"],
        "response": "I am a multi-featured, language-agnostic chatbot built with Python for a university project!"
    },
    "capabilities": {
        "keywords": ["what can you do", "features", "help", "options", "what do you do"],
        "response": "I can chat in multiple languages, solve math expressions (e.g., 25 * 4), look up word definitions (e.g., define algorithm), and answer basic questions!"
    },
    "farewell": {
        "keywords": ["bye", "goodbye", "see you", "exit", "cya"],
        "response": "Goodbye! Have a fantastic day ahead!"
    }
}

def process_intent(english_text):
    text_lower = english_text.lower().strip()

    # Feature 1: Dictionary Lookup
    if "define" in text_lower or "meaning of" in text_lower:
        words = text_lower.split()
        return fetch_definition(words[-1])

    # Feature 2: Math Expressions
    if any(char in text_lower for char in ['+', '-', '*', '/']) and any(c.isdigit() for c in text_lower):
        math_result = evaluate_math(text_lower)
        if math_result:
            return math_result

    # Feature 3: Match intent against Knowledge Base
    for intent, data in KNOWLEDGE_BASE.items():
        for keyword in data["keywords"]:
            if keyword in text_lower or text_lower in keyword:
                return data["response"]

    # Fallback
    return "I'm a simple rule-based bot, so I might not know that yet! Try asking me 'what can you do', a math problem like '12 + 15', or 'define python'."

# -------------------------------------------------------------------
# Chat Interface Logic
# -------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

st.sidebar.header("Chatbot Settings")
language_options = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Chinese (Simplified)": "zh-cn",
    "Japanese": "ja"
}
selected_language_name = st.sidebar.selectbox("Preferred Output Language:", list(language_options.keys()))
target_lang_code = language_options[selected_language_name]

if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if user_input := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 1. Translate input to English
    english_input = translate_to_english(user_input)
    
    # 2. Get Response
    english_reply = process_intent(english_input)
    
    # 3. Translate back to selected language
    final_reply = translate_from_english(english_reply, target_lang_code)

    st.session_state.messages.append({"role": "assistant", "content": final_reply})
    with st.chat_message("assistant"):
        st.markdown(final_reply)
