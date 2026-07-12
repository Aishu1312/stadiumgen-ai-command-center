import streamlit as st
import streamlit.components.v1 as components
from components.ui import render_header, render_toast
from services.ai_service import generate_response_stream
import logging

logger = logging.getLogger(__name__)

# Safe initialization
if "current_page_context" not in st.session_state:
    st.session_state.current_page_context = ""
st.session_state.current_page_context = "User is on the Accessibility page, testing accessibility features."

# Initialize accessibility state keys if missing
default_states = {
    "acc_high_contrast": False,
    "acc_dyslexia_font": False,
    "acc_reading_mode": False,
    "acc_ruler": False,
    "acc_text_size": 1.0,
    "acc_spacing": 1.0,
}
for key, default_val in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = default_val

def inject_accessibility_css():
    """Injects dynamic CSS based on session state toggles."""
    css_rules = []
    
    # 1. High Contrast Mode
    if st.session_state.get("acc_high_contrast"):
        # Apply a high contrast filter to the main container
        css_rules.append("""
        .stApp {
            filter: contrast(150%) saturate(150%);
            background-color: #000000 !important;
            color: #FFFFFF !important;
        }
        .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp label, .stApp span, .stApp div {
            color: #FFFFFF !important;
        }
        .glass-card {
            background: rgba(20, 20, 20, 0.95) !important;
            border: 1px solid #FFFFFF !important;
            box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1) !important;
        }
        """)
        
    # 2. Dyslexia Font
    if st.session_state.get("acc_dyslexia_font"):
        css_rules.append("""
        @import url('https://fonts.cdnfonts.com/css/opendyslexic');
        * {
            font-family: 'OpenDyslexic', sans-serif !important;
        }
        """)
        
    # 3. Reading Mode (focus)
    if st.session_state.get("acc_reading_mode"):
        css_rules.append("""
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        .stApp {
            max-width: 800px;
            margin: 0 auto;
        }
        """)
        
    # 4. Spacing and Text Size
    text_size = st.session_state.get("acc_text_size", 1.0)
    spacing = st.session_state.get("acc_spacing", 1.0)
    if text_size != 1.0 or spacing != 1.0:
        css_rules.append(f"""
        .stApp, p, h1, h2, h3, h4, h5, h6, label, span, div {{
            font-size: calc(1rem * {text_size}) !important;
            line-height: calc(1.5 * {spacing}) !important;
            letter-spacing: calc(0.05em * {spacing}) !important;
        }}
        """)
        
    # 5. Focus indicators for WCAG keyboard navigation
    css_rules.append("""
    *:focus-visible {
        outline: 3px solid #ffaa00 !important;
        outline-offset: 2px !important;
    }
    """)

    if css_rules:
        combined_css = "\n".join(css_rules)
        st.markdown(f"<style>{combined_css}</style>", unsafe_allow_html=True)


def inject_accessibility_js():
    """Injects JavaScript for features like Reading Ruler and TTS."""
    js_code = """
    <script>
    // 1. Reading Ruler
    (function() {
        let existingRuler = document.getElementById('acc-reading-ruler');
        if (existingRuler) {
            existingRuler.remove();
        }
        const isRulerActive = """ + str(st.session_state.get('acc_ruler', False)).lower() + """;
        if (isRulerActive) {
            const ruler = document.createElement('div');
            ruler.id = 'acc-reading-ruler';
            ruler.style.position = 'fixed';
            ruler.style.left = '0';
            ruler.style.width = '100%';
            ruler.style.height = '40px';
            ruler.style.backgroundColor = 'rgba(255, 255, 0, 0.2)';
            ruler.style.borderTop = '2px solid rgba(255, 200, 0, 0.8)';
            ruler.style.borderBottom = '2px solid rgba(255, 200, 0, 0.8)';
            ruler.style.pointerEvents = 'none';
            ruler.style.zIndex = '999999';
            ruler.style.display = 'none';
            document.body.appendChild(ruler);

            document.addEventListener('mousemove', function(e) {
                ruler.style.display = 'block';
                ruler.style.top = (e.clientY - 20) + 'px';
            });
        }
    })();
    </script>
    """
    components.html(js_code, height=0, width=0)


def display_accessibility():
    render_header("Smart Accessibility Center", "Ensuring an inclusive experience for everyone")
    
    # Inject active styles and scripts
    inject_accessibility_css()
    inject_accessibility_js()

    st.markdown("### 🛠️ Control Panel")
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='glass-card' style='padding: 20px; border-radius: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("#### 👁️ Visual Accommodations")
        st.toggle("High Contrast Mode (Color Blind Safe)", key="acc_high_contrast")
        st.toggle("Dyslexia-friendly Font", key="acc_dyslexia_font")
        st.toggle("Focus / Reading Mode (Hides Sidebar)", key="acc_reading_mode")
        st.toggle("Interactive Reading Ruler", key="acc_ruler")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card' style='padding: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
        st.markdown("#### 📏 Layout & Spacing")
        st.slider("Text Size Multiplier", min_value=0.8, max_value=2.0, value=1.0, step=0.1, key="acc_text_size")
        st.slider("Line & Letter Spacing", min_value=0.8, max_value=2.0, value=1.0, step=0.1, key="acc_spacing")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card' style='padding: 20px; border-radius: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("#### 🔊 Audio & AI Guidance")
        
        guidance_topic = st.selectbox(
            "Select an accessibility topic for an AI-generated guide:", 
            [
                "Stadium Entry Process for Wheelchairs", 
                "Finding Quiet Rooms for Autism Support",
                "Visual Impairment Navigational Beacons",
                "Sensory Bag Pickup Locations"
            ],
            help="Choose a topic to receive a simplified, step-by-step audio-ready script."
        )
        
        if st.button("Generate Explanation", use_container_width=True):
            st.markdown("##### Guide Script")
            prompt = f"Provide a clear, easy-to-understand, step-by-step guide on: {guidance_topic}. Use simple language suitable for cognitive accessibility. Keep it under 150 words."
            
            try:
                stream = generate_response_stream(prompt)
                full_response = st.write_stream(stream)
                
                # Render a TTS button via HTML for the generated text
                escaped_response = full_response.replace("'", "\\'").replace('"', '\\"').replace("\\n", " ")
                tts_script = f"""
                <div style="text-align: center; margin-top: 10px;">
                    <button onclick="window.speechSynthesis.speak(new SpeechSynthesisUtterance('{escaped_response}'));" 
                            style="padding: 10px 20px; border-radius: 5px; background-color: #007bff; color: white; border: none; cursor: pointer; font-size: 16px;">
                        🔊 Read Aloud
                    </button>
                    <button onclick="window.speechSynthesis.cancel();" 
                            style="padding: 10px 20px; border-radius: 5px; background-color: #dc3545; color: white; border: none; cursor: pointer; font-size: 16px; margin-left: 10px;">
                        ⏹️ Stop
                    </button>
                </div>
                """
                components.html(tts_script, height=60)
                
                st.success("🔊 Text-to-Speech is ready. Click the Read Aloud button above.")
                render_toast("Audio guide generated.", "✅")
            except Exception as e:
                logger.error(f"Error generating accessibility guide: {e}")
                st.error("Failed to generate the guide. Please check your AI API key configuration.")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("---")
    
    st.markdown("### 🎙️ Speech-to-Text & Voice Commands")
    st.markdown("We support native OS voice dictation for all inputs. Ensure you are in a quiet environment.")
    st.text_input("Speak or Type your command here:", 
                  placeholder="e.g. Where is the nearest sensory room?", 
                  help="Use your device's native dictation (Windows Key + H on Windows, or double-tap Fn on Mac) to use Speech-to-Text.", 
                  key="acc_stt")

    st.markdown("---")
    
    st.markdown("### 🗺️ Accessibility Maps")
    st.markdown("We are committed to providing an inclusive environment. View our accessible zones below.")
    try:
        # Fixed use_column_width deprecation by changing to use_container_width
        st.image("https://images.unsplash.com/photo-1579294528148-18e38d4e9411?q=80&w=600&auto=format&fit=crop", 
                 caption="Wheelchair Accessible Zones and Sensory Rooms", 
                 use_container_width=True)
    except Exception as e:
        logger.error(f"Failed to load accessibility map image: {e}")
        st.warning("Accessibility map image is currently unavailable.")

display_accessibility()
