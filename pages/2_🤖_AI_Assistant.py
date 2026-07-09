import streamlit as st
from ai.gemini_client import generate_response
from components.ui import render_header

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

render_header("AI Stadium Assistant", "Your GenAI-powered intelligent companion")

if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # Initial Greeting
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I am your AI Stadium Assistant for the FIFA World Cup 2026. How can I help you today? (e.g., 'Where is my gate?', 'Nearest food court?')"
    })

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about the stadium..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        system_instruction = """
        You are a highly intelligent AI Stadium Assistant for the FIFA World Cup 2026. 
        You know everything about the stadium layout, gates, food courts, parking, and emergencies.
        Be concise, helpful, and polite.
        """
        
        full_response = generate_response(prompt, system_instruction=system_instruction)
        message_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
