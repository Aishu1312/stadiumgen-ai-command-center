# Bug Report

| Issue | Root Cause | File | Fix Applied | Verification |
|-------|------------|------|-------------|--------------|
| `set_page_config` Error | Streamlit decorators like `@st.cache_data` in imported modules were executing before `st.set_page_config()` | `app.py`, `pages/*.py` | Moved `set_page_config` to line 2 in all files | Passed |
| Missing Session State | `init_session_state()` was only called in `app.py`, causing `KeyError` on direct page links | `app.py` | Extracted to `utils/session.py` and injected in all pages | Passed |
| AI API Key Crash | `services/ai_service.py` relied strictly on `st.secrets` without fallback | `services/ai_service.py` | Added environment variable checks, exception handling, and simulated response fallbacks | Passed |
| FOUC (Flash of Unstyled Content) | Streamlit loaded default light theme before CSS was injected | `.streamlit/config.toml` | Created config file enforcing Dark Theme natively | Passed |
