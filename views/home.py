import streamlit as st
from components.ui import render_header, render_metric, show_loading_skeleton, render_toast
from services.data_service import generate_sustainability_metrics
from services.ai_service import generate_response_stream, AIError

# Set context for AI Assistant
st.session_state.current_page_context = "User is currently on the Home page, viewing the high-level dashboard and quick actions."

def display_home():
    render_header("Stadium Command Center", "Live Overview of WorldCup 2026 Operations")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric("Total Visitors", "84,521", "+2,100 since last hour", "success")
    with col2:
        render_metric("Active Incidents", "3", "-2 resolved recently", "danger")
    with col3:
        render_metric("Avg Queue Time", "12 mins", "Normal", "success")
    with col4:
        score = generate_sustainability_metrics().get("energy_saved_kwh", 0)
        render_metric("Eco Score", f"{score/100:.0f}/100", "Excellent", "success")

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("### 🏟️ Quick Actions")
    col_a, col_b, col_c, col_d = st.columns(4)
    
    action_result = None
    
    with col_a:
        if st.button("Generate Report", use_container_width=True):
            action_result = "Report"
            render_toast("Report generated successfully!", "✅")
    with col_b:
        if st.button("Broadcast Announcement", use_container_width=True):
            action_result = "Broadcast Announcement"
            render_toast("Broadcast channel opened.", "🔊")
    with col_c:
        if st.button("Lockdown Protocol", use_container_width=True):
            action_result = "Lockdown Protocol"
            render_toast("CRITICAL: Lockdown engaged.", "🚨")
    with col_d:
        if st.button("Dispatch Medics", use_container_width=True):
            action_result = "Dispatch Medics"
            render_toast("Medics en route.", "🚑")

    if action_result:
        st.markdown("---")
        st.markdown(f"### 🤖 AI Agent: {action_result}")
        
        prompt = ""
        if action_result == "Report":
            prompt = "Generate a short evening operations report for the stadium. Include total visitors, any resolved incidents, and sustainability performance."
        elif action_result == "Broadcast Announcement":
            prompt = "Generate a polite, welcoming broadcast announcement for the stadium crowd thanking them for attending and wishing them a safe journey home."
        elif action_result == "Lockdown Protocol":
            prompt = "Generate a strict, clear emergency lockdown announcement instructing all patrons to remain seated and await security instructions."
        elif action_result == "Dispatch Medics":
            prompt = "Generate a brief radio dispatch message to the medical team directing them to Zone A for an immediate medical emergency."
            
        try:
            stream = generate_response_stream(prompt)
            st.write_stream(stream)
        except AIError as e:
            st.error(f"🚨 Error: {e}")
        except Exception as e:
            st.error("🚨 Error: An unexpected error occurred.")

display_home()
