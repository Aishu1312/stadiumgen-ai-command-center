import streamlit as st
import streamlit.components.v1 as components
from components.ui import render_header, render_toast
from services.ai_service import generate_response_stream
from services.exceptions import AIError
from gtts import gTTS
import io
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
        
        if "acc_guide_text" not in st.session_state:
            st.session_state.acc_guide_text = ""
        if "acc_audio_bytes" not in st.session_state:
            st.session_state.acc_audio_bytes = None
        if "acc_play_audio" not in st.session_state:
            st.session_state.acc_play_audio = False
            
        is_processing = st.session_state.get('is_processing', False)
        if st.button("Generate Explanation", use_container_width=True, disabled=is_processing):
            if st.session_state.get('is_processing', False):
                st.warning("⏳ Please wait for the current request to complete.")
            else:
                st.session_state.is_processing = True
                try:
                    st.session_state.acc_guide_text = ""
                    st.session_state.acc_audio_bytes = None
                    st.session_state.acc_play_audio = False
                    
                    st.markdown("##### Guide Script")
                    prompt = f"Provide a clear, easy-to-understand, step-by-step guide on: {guidance_topic}. Use simple language suitable for cognitive accessibility. Keep it under 150 words."
                    
                    with st.spinner("Generating accessibility guide..."):
                        stream = generate_response_stream(prompt)
                        full_response = st.write_stream(stream)
                        st.session_state.acc_guide_text = full_response
                except AIError as e:
                    logger.error(f"Error generating accessibility guide: {e}")
                    st.error(f"🚨 Error: {e}")
                except Exception as e:
                    logger.error(f"Error generating accessibility guide: {e}")
                    st.error("🚨 Error: An unexpected error occurred.")
                finally:
                    st.session_state.is_processing = False
                
        elif st.session_state.acc_guide_text:
            st.markdown("##### Guide Script")
            st.markdown(st.session_state.acc_guide_text)
            
        if st.session_state.acc_guide_text:
            
            st.markdown("---")
            st.markdown("##### Text-to-Speech Ready")
            st.markdown("Click the Read Aloud button to begin audio playback.")
            
            col_play, col_stop = st.columns(2)
            with col_play:
                if st.button("🔊 Read Aloud", use_container_width=True):
                    st.session_state.acc_play_audio = True
                    if not st.session_state.acc_audio_bytes:
                        try:
                            with st.spinner("Generating audio..."):
                                tts = gTTS(st.session_state.acc_guide_text, lang='en')
                                audio_fp = io.BytesIO()
                                tts.write_to_fp(audio_fp)
                                st.session_state.acc_audio_bytes = audio_fp.getvalue()
                        except Exception as e:
                            logger.error(f"gTTS error: {e}")
                            st.error("Could not generate audio.")
                            st.session_state.acc_play_audio = False

            with col_stop:
                if st.button("⏹️ Stop", use_container_width=True):
                    # Streamlit limitation: Browser autoplay restrictions and limited JS interop mean we cannot invoke 
                    # a true 'stop' method on an active st.audio component mid-playback.
                    # By toggling acc_play_audio to False, Streamlit unmounts the component on rerun, effectively resetting it.
                    st.session_state.acc_play_audio = False

            if st.session_state.acc_play_audio and st.session_state.acc_audio_bytes:
                st.audio(st.session_state.acc_audio_bytes, format="audio/mp3", autoplay=True)
                render_toast("Audio is playing...", "🔊")
                
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
        # Wrap the image in a styled div
        st.markdown(
            """
            <style>
            .map-container {
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                border: 1px solid rgba(255,255,255,0.1);
                margin: 20px 0;
            }
            .map-container img {
                transition: transform 0.3s ease;
            }
            .map-container:hover img {
                transform: scale(1.02);
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        st.image("assets/accessibility_map.png", 
                 caption="Premium Stadium Accessibility Map & Inclusive Zones", 
                 use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Failed to load accessibility map image: {e}")
        st.warning("Accessibility map image is currently unavailable.")

    st.markdown("---")
    
    # Task 3: GitHub Repository Section
    st.markdown("### 📂 Project Repository")
    repo_html = """
<a href="https://github.com/Aishu1312/banknova-ai-digital-wealth-management" target="_blank" style="text-decoration: none;">
    <div style="
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        display: flex;
        align-items: center;
        gap: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        cursor: pointer;
    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 15px 35px rgba(0,0,0,0.3)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 10px 25px rgba(0,0,0,0.2)';">
        <div style="
            background: rgba(255,255,255,0.1);
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <svg height="32" viewBox="0 0 16 16" width="32" fill="white">
                <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
            </svg>
        </div>
        <div style="flex: 1;">
            <h4 style="margin: 0; color: #ffffff; font-size: 18px; font-weight: 600;">BankNova AI Digital Wealth Management</h4>
            <p style="margin: 6px 0 0 0; color: rgba(255,255,255,0.7); font-size: 14px;">Explore the source code on GitHub ↗</p>
        </div>
    </div>
</a>
"""
    st.markdown(repo_html, unsafe_allow_html=True)

display_accessibility()
