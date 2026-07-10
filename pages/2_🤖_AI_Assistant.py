import streamlit as st

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

from utils.session import init_session_state
init_session_state()
from services.ai_service import generate_response_stream
from components.ui import render_header


def display_chat():
    render_header("AI Stadium Assistant", "Your GenAI-powered intelligent companion")

    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I am your AI Stadium Assistant for the FIFA World Cup 2026. How can I help you today? (e.g., 'Where is my gate?', 'Nearest food court?')"
        }]

    # Render history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything about the stadium..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            sys_prompt = "You are a highly intelligent AI Stadium Assistant. Provide concise, helpful, and polite answers."
            
            # Stream the response natively
            response_stream = generate_response_stream(prompt, system_instruction=sys_prompt)
            full_response = st.write_stream(response_stream)
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    display_chat()
