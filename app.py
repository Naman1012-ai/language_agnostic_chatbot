import streamlit as st
from google import genai
from google.genai import types

# -------------------------------------------------------------------
# Page Configuration
# -------------------------------------------------------------------
st.set_page_config(page_title="Language Agnostic AI Chatbot", page_icon="🤖")
st.title("🤖 Multi-Feature Language Agnostic Chatbot")
st.caption("Built with Python & Streamlit | Powered by Gemini AI")

# Sidebar for Setup
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

language_options = [
    "Auto-Detect / Native Language",
    "English",
    "Spanish",
    "French",
    "German",
    "Hindi",
    "Chinese",
    "Japanese"
]
selected_language = st.sidebar.selectbox("Preferred Response Language:", language_options)

if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

# -------------------------------------------------------------------
# Chat Memory Setup (Stateful Conversation)
# -------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous conversation thread
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------------------------------------------------------
# Interactive Chat Loop
# -------------------------------------------------------------------
if user_input := st.chat_input("Ask me anything in any language..."):
    # Render user input
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("Please enter your Gemini API Key in the sidebar to start chatting!")
    else:
        try:
            client = genai.Client(api_key=api_key)

            # Define System Persona & Language Rules
            system_instruction = (
                "You are a helpful, polite, and intelligent AI chatbot assistant built for a university project. "
                "You are language-agnostic. Understand user messages in whatever language they speak. "
            )
            if selected_language != "Auto-Detect / Native Language":
                system_instruction += f"Always translate and respond in {selected_language}."
            else:
                system_instruction += "Respond in the same language the user spoke to you in."

            # Convert Streamlit history to Gemini Content Objects so it remembers context (like names)
            formatted_contents = []
            for msg in st.session_state.messages:
                role_type = "user" if msg["role"] == "user" else "model"
                formatted_contents.append(
                    types.Content(
                        role=role_type,
                        parts=[types.Part.from_text(text=msg["content"])]
                    )
                )

            # Generate response with conversation history
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=formatted_contents,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction
                        )
                    )
                    reply_text = response.text
                    st.markdown(reply_text)

            # Save assistant reply to session memory
            st.session_state.messages.append({"role": "assistant", "content": reply_text})

        except Exception as e:
            with st.chat_message("assistant"):
                st.error(f"Error generating response: {e}")
