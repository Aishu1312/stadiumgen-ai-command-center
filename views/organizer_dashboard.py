import streamlit as st
import pandas as pd
from components.ui import render_header, render_metric, show_loading_skeleton
from services.ai_service import generate_response_stream
from services.exceptions import AIError
from config.constants import Prompts

st.session_state.current_page_context = "User is on the Organizer Dashboard, viewing high-level metrics and predicting footfall."

def display_organizer():
    render_header("Organizer Dashboard", "Executive insights and predictive analytics")

    st.markdown("### 📈 Live Analytics")
    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric("Total Volunteers Active", "1,240", "Optimal", "success")
    with col2:
        render_metric("Total Merchandise Sales", "$2.4M", "+15% vs yesterday", "success")
    with col3:
        render_metric("Overall Satisfaction", "4.8/5.0", "Based on AI sentiment", "info")

    st.markdown("<hr class='styled-hr'>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🔮 Predictive Footfall")
        df_trend = pd.DataFrame({
            "Time": pd.date_range(start="2026-07-09 10:00", periods=10, freq="h"),
            "Visitors": [5000, 12000, 25000, 40000, 60000, 80000, 84000, 82000, 45000, 15000]
        })
        try:
            import plotly.express as px
            fig = px.area(df_trend, x="Time", y="Visitors", template="plotly_dark", color_discrete_sequence=["#3b82f6"])
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=10, l=10, r=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
             st.error("Missing dependency: plotly.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🤖 Ask AI for Insights")
        question = st.text_input("Ask a question about the stadium data:", placeholder="e.g., How can we reduce queue times at Gate 2?")
        is_processing = st.session_state.get('is_processing', False)
        if st.button("Get AI Insight", use_container_width=True, disabled=is_processing):
            if question:
                if st.session_state.get('is_processing', False):
                    st.warning("⏳ Please wait for the current request to complete.")
                else:
                    st.session_state.is_processing = True
                    try:
                        st.markdown("#### Insight")
                        with st.spinner("Connecting to AI..."):
                            stream = generate_response_stream(question, system_instruction=Prompts.SYSTEM_ORGANIZER_INSIGHTS)
                            st.write_stream(stream)
                    except AIError as e:
                        st.error(f"🚨 Error: {e}")
                    except Exception as e:
                        st.error("🚨 Error: An unexpected error occurred.")
                    finally:
                        st.session_state.is_processing = False
            else:
                st.warning("Please enter a question.")
        st.markdown("</div>", unsafe_allow_html=True)

display_organizer()
