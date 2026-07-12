import streamlit as st
from components.ui import render_header, render_toast, show_loading_skeleton
from services.data_service import generate_transport_data
from services.ai_service import generate_response_stream
from services.exceptions import AIError

st.session_state.current_page_context = "User is viewing the Transport Planner page to check train/bus statuses and ask for travel advice."

def display_transport():
    render_header("AI Transportation Planner", "Predictive routing and live transit status")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🚏 Live Transport Status")
        df_transport = generate_transport_data()
        
        # Display with cleaner styled dataframe using Pandas Styler
        styled_df = df_transport.style.map(
            lambda x: 'background-color: rgba(239, 68, 68, 0.2); color: #f87171; font-weight: bold;' if x == 'Delayed' else 
                      'background-color: rgba(16, 185, 129, 0.2); color: #34d399;' if x == 'On Time' else 
                      'background-color: rgba(245, 158, 11, 0.2); color: #fbbf24;',
            subset=['Status']
        )
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🤖 Ask AI for Travel Advice")
        user_loc = st.text_input("Your Location:", placeholder="e.g., Downtown Hotel")
        
        is_processing = st.session_state.get('is_processing', False)
        if st.button("Generate Recommendation", use_container_width=True, disabled=is_processing):
            if user_loc:
                if st.session_state.get('is_processing', False):
                    st.warning("⏳ Please wait for the current request to complete.")
                else:
                    st.session_state.is_processing = True
                    try:
                        st.markdown("#### Recommendations")
                        prompt = f"Provide a travel recommendation from {user_loc} to the World Cup Stadium. Suggest the fastest route, the most eco-friendly route, and expected travel time."
                        
                        with st.spinner("Generating response..."):
                            # Streaming the AI response natively
                            stream = generate_response_stream(prompt)
                            st.write_stream(stream)
                        render_toast("Recommendation completed.", "🚍")
                    except AIError as e:
                        st.error(f"🚨 Error: {e}")
                    except Exception as e:
                        st.error("🚨 Error: An unexpected error occurred.")
                    finally:
                        st.session_state.is_processing = False
            else:
                st.warning("Please enter your location.")
        st.markdown("</div>", unsafe_allow_html=True)

display_transport()
