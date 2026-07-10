# Changelog

## [2.1.0] - 2026-07-10

### Added
- Created `utils/session.py` to centralize Streamlit session state initialization.
- Added `packages.txt` for OS-level dependencies (`build-essential`).
- Added `.streamlit/config.toml` for native theming.
- Added custom CSS animations for skeleton loading in `assets/style.css`.
- Added robust logging and fallback UI to `services/ai_service.py`.

### Fixed
- Fixed critical runtime `StreamlitAPIException` by moving `st.set_page_config` to the very top of `app.py` and all 10 page scripts.
- Fixed `KeyError` crashes on direct page loads by injecting session state initialization globally.
- Fixed AI Service crashing when API key is missing by adding `os.environ` fallback and simulated responses.

### Changed
- Upgraded `show_loading_skeleton` in `components/ui.py` to use animated CSS skeletons.
- Improved Streamlit Cloud compatibility.
