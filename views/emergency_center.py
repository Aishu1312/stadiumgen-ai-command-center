import streamlit as st
from components.ui import render_header, render_toast
from services.data_service import generate_incidents
from services.ai_service import generate_emergency_sop
from services.exceptions import AIError

st.session_state.current_page_context = "User is on the Emergency Center page, monitoring live incidents and generating SOPs."

def display_emergency():
    render_header("Emergency AI Command", "Live incident tracking and automated SOP generation")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🚨 Active Incidents")
        df_incidents = generate_incidents()
        
        styled_df = df_incidents.style.map(
            lambda x: 'background-color: rgba(239, 68, 68, 0.2); color: #f87171; font-weight: bold;' if x == 'Pending' else 
                      'background-color: rgba(16, 185, 129, 0.2); color: #34d399;' if x == 'Resolved' else 
                      'background-color: rgba(245, 158, 11, 0.2); color: #fbbf24;',
            subset=['Status']
        )
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📜 Generate AI SOP")
        incident_type = st.selectbox("Incident Type:", ["Medical Emergency", "Fire", "Lost Child", "Security Threat", "Crowd Panic"])
        location = st.text_input("Location:", placeholder="e.g., Gate 4, Section 102")
        
        is_processing = st.session_state.get('is_processing', False)
        if st.button("Generate Action Checklist", type="primary", use_container_width=True, disabled=is_processing):
            if location:
                if st.session_state.get('is_processing', False):
                    st.warning("⏳ Please wait for the current request to complete.")
                else:
                    st.session_state.is_processing = True
                    try:
                        with st.spinner("AI is generating Emergency SOP..."):
                            sop = generate_emergency_sop(incident_type, location)
                            st.error("🚨 EMERGENCY SOP GENERATED 🚨")
                            st.markdown(sop)
                            render_toast(f"SOP generated for {incident_type}", "🚨")
                    except AIError as e:
                        st.error(f"🚨 Error: {e}")
                    except Exception as e:
                        st.error("🚨 Error: An unexpected error occurred.")
                    finally:
                        st.session_state.is_processing = False
            else:
                st.warning("Please provide a location to generate the SOP.")
        st.markdown("</div>", unsafe_allow_html=True)

display_emergency()
