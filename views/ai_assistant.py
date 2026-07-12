import streamlit as st
from services.ai_service import generate_response_stream
from services.exceptions import AIError
from components.ui import render_header

st.session_state.current_page_context = "User is currently using the dedicated AI Assistant page for general stadium queries."

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

    is_processing = st.session_state.get('is_processing', False)
    if prompt := st.chat_input("Ask me anything about the stadium...", disabled=is_processing):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            sys_prompt = "You are a highly intelligent AI Stadium Assistant. Provide concise, helpful, and polite answers."
            
            st.session_state.is_processing = True
            try:
                # Stream the response natively
                response_stream = generate_response_stream(prompt, system_instruction=sys_prompt)
                full_response = st.write_stream(response_stream)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except AIError as e:
                st.error(f"🚨 Error: {e}")
            except Exception as e:
                st.error("🚨 Error: An unexpected error occurred.")
            finally:
                st.session_state.is_processing = False

display_chat()
