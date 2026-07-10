import streamlit as st

st.set_page_config(page_title="Accessibility", page_icon="♿", layout="wide")

from utils.session import init_session_state
init_session_state()
from components.ui import render_header, render_toast
from services.ai_service import generate_response_stream


def display_accessibility():
    render_header("Smart Accessibility Assistant", "Ensuring an inclusive experience for everyone")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🔊 Text-to-Speech & Guidance")
        st.info("Simulated Screen Reader Mode Active. Large Text Mode Enabled.")
        
        guidance_topic = st.selectbox("Select a topic for detailed AI explanation:", 
                                      ["Stadium Entry Process for Wheelchairs", 
                                       "Finding Quiet Rooms for Autism Support",
                                       "Visual Impairment Navigational Beacons"])
        
        if st.button("Generate Explanation", use_container_width=True):
            st.markdown("#### Audio Script")
            prompt = f"Provide a clear, easy-to-understand, step-by-step guide on: {guidance_topic}. Use simple language suitable for accessibility purposes."
            
            stream = generate_response_stream(prompt)
            st.write_stream(stream)
            
            st.success("🔊 Audio narration ready (simulated).")
            render_toast("Audio guide generated.", "✅")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🛠️ Quick Accessibility Toggles")
        
        st.toggle("High Contrast Mode (Color Blind Safe)", value=True)
        st.toggle("Large Text Mode")
        st.toggle("Enable Sign Language Avatar (Simulated)")
        st.toggle("Easy Language Mode (Simplified text)")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        try:
            st.image("https://images.unsplash.com/photo-1579294528148-18e38d4e9411?q=80&w=600&auto=format&fit=crop", caption="Wheelchair Accessible Zones", use_column_width=True)
        except Exception:
            pass

if __name__ == "__main__":
    display_accessibility()
