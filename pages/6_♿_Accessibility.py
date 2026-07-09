import streamlit as st
from components.ui import render_header
from ai.gemini_client import generate_response

st.set_page_config(page_title="Accessibility", page_icon="♿", layout="wide")

render_header("Smart Accessibility Assistant", "Ensuring an inclusive experience for everyone")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔊 Text-to-Speech & Guidance")
    st.info("Simulated Screen Reader Mode Active. Large Text Mode Enabled.")
    
    guidance_topic = st.selectbox("Select a topic for detailed AI explanation:", 
                                  ["Stadium Entry Process for Wheelchairs", 
                                   "Finding Quiet Rooms for Autism Support",
                                   "Visual Impairment Navigational Beacons"])
    
    if st.button("Generate Explanation"):
        with st.spinner("Generating accessible explanation..."):
            prompt = f"Provide a clear, easy-to-understand, step-by-step guide on: {guidance_topic}. Use simple language suitable for accessibility purposes."
            explanation = generate_response(prompt)
            st.write(explanation)
            st.success("🔊 Audio narration ready (simulated).")

with col2:
    st.markdown("### 🛠️ Quick Accessibility Toggles")
    
    st.toggle("High Contrast Mode (Color Blind Safe)", value=True)
    st.toggle("Large Text Mode")
    st.toggle("Enable Sign Language Avatar (Simulated)")
    st.toggle("Easy Language Mode (Simplified text)")
    
    st.markdown("---")
    st.image("https://images.unsplash.com/photo-1579294528148-18e38d4e9411?q=80&w=600&auto=format&fit=crop", caption="Wheelchair Accessible Zones", use_column_width=True)
