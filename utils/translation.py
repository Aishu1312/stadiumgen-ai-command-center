import streamlit as st
import functools
import re
from streamlit.delta_generator import DeltaGenerator
from utils.translation_dict import TRANSLATIONS

LANG_MAP = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "Arabic": "ar",
    "Portuguese": "pt",
    "Hindi": "hi",
    "Japanese": "ja",
    "German": "de",
    "Italian": "it",
    "Chinese": "zh"
}

def extract_decorations(text: str) -> tuple[str, str, str]:
    """
    Extracts leading markdown symbols/emojis and trailing symbols/emojis.
    Returns (prefix, clean_text, suffix).
    Since original texts in the source code are in English, we search for the first
    and last alphanumeric character to locate the core content.
    """
    match_start = re.search(r'[A-Za-z0-9]', text)
    if not match_start:
        return "", text, ""
        
    start_idx = match_start.start()
    prefix = text[:start_idx]
    remainder = text[start_idx:]
    
    match_end = list(re.finditer(r'[A-Za-z0-9]', remainder))
    if not match_end:
        return prefix, remainder, ""
        
    end_idx = match_end[-1].end()
    clean_text = remainder[:end_idx]
    suffix = remainder[end_idx:]
    
    return prefix, clean_text, suffix

def is_html_or_css(text: str) -> bool:
    """Checks if a string is raw HTML/CSS/JavaScript structure to avoid translating it."""
    text_stripped = text.strip()
    if not text_stripped:
        return False
    
    # If the string contains HTML tags (e.g. <div, <span, <h1, <hr, <br, </div etc.)
    if re.search(r'<[a-zA-Z/][^>]*>', text_stripped):
        return True
        
    # Styles, scripts, and SVGs
    if ("<style>" in text_stripped or "</style>" in text_stripped or
        "<script>" in text_stripped or "</script>" in text_stripped or
        "<svg" in text_stripped or
        "background-color:" in text_stripped or
        "style=" in text_stripped):
        return True
        
    # Simple formatting tags or dividers
    if text_stripped in ["---", "***", "___"]:
        return True
        
    return False

def translate_if_needed(text: str, is_widget: bool = False) -> str:
    """Translates text to st.session_state.language if not English."""
    if not isinstance(text, str) or not text.strip():
        return text
        
    target_lang = st.session_state.get("language", "English")
    if target_lang == "English":
        return text
        
    # Preserve formatting (newlines, leading/trailing spaces)
    leading = text[:len(text) - len(text.lstrip())]
    trailing = text[len(text.rstrip()):]
    text_clean = text.strip()
    
    # 1. Match against static translations (exact trimmed text)
    if text_clean in TRANSLATIONS and target_lang in TRANSLATIONS[text_clean]:
        return leading + TRANSLATIONS[text_clean][target_lang] + trailing
        
    # 2. Extract decorations and match cleaned inner text
    prefix, clean_inner, suffix = extract_decorations(text_clean)
    if clean_inner and clean_inner != text_clean:
        if clean_inner in TRANSLATIONS and target_lang in TRANSLATIONS[clean_inner]:
            return leading + prefix + TRANSLATIONS[clean_inner][target_lang] + suffix + trailing
            
    # 3. Match markdown headers specifically
    match_hdr = re.match(r'^([#\s]+)(.*)$', text_clean)
    if match_hdr:
        hdr_prefix = match_hdr.group(1)
        hdr_content = match_hdr.group(2).strip()
        if hdr_content in TRANSLATIONS and target_lang in TRANSLATIONS[hdr_content]:
            return leading + hdr_prefix + TRANSLATIONS[hdr_content][target_lang] + trailing
            
        h_prefix, h_clean, h_suffix = extract_decorations(hdr_content)
        if h_clean in TRANSLATIONS and target_lang in TRANSLATIONS[h_clean]:
            return leading + hdr_prefix + h_prefix + TRANSLATIONS[h_clean][target_lang] + h_suffix + trailing

    # 4. Skip translating code, styling, or HTML strings
    if is_html_or_css(text):
        return text
        
    # 5. Skip LLM translation for widgets (buttons, labels, selectboxes, placeholders) to ensure snappiness
    if is_widget:
        return text
        
    # 6. Fall back to AI translation dynamically for page content
    try:
        from services.ai_service import translate_text
        translated = translate_text(text_clean, target_lang)
        return leading + translated + trailing
    except Exception:
        return text

def patch_delta_generator_method(method_name: str, arg_index: int = 0, is_kwarg: str = None, has_options: bool = False, is_widget: bool = False):
    """Utility to monkeypatch standard DeltaGenerator display methods."""
    orig_method = getattr(DeltaGenerator, method_name, None)
    if not orig_method:
        return
        
    @functools.wraps(orig_method)
    def wrapper(self, *args, **kwargs):
        target_lang = st.session_state.get("language", "English")
        if target_lang == "English":
            return orig_method(self, *args, **kwargs)
            
        new_args = list(args)
        
        # Translate main positional or keyword argument
        if len(new_args) > arg_index:
            val = new_args[arg_index]
            if isinstance(val, str):
                new_args[arg_index] = translate_if_needed(val, is_widget=is_widget)
        elif is_kwarg and is_kwarg in kwargs:
            val = kwargs[is_kwarg]
            if isinstance(val, str):
                kwargs[is_kwarg] = translate_if_needed(val, is_widget=is_widget)
                
        # Translate standard kwargs if present
        if "placeholder" in kwargs and isinstance(kwargs["placeholder"], str):
            kwargs["placeholder"] = translate_if_needed(kwargs["placeholder"], is_widget=True)
            
        if "help" in kwargs and isinstance(kwargs["help"], str):
            kwargs["help"] = translate_if_needed(kwargs["help"], is_widget=True)
            
        # Translate selection options (selectbox / radio)
        if has_options:
            label = kwargs.get("label")
            if not label and len(args) > 0:
                label = args[0]
            # Bypass translating default application language selectbox options here
            if label != "Default Application Language":
                options_index = 1
                if len(new_args) > options_index:
                    options = new_args[options_index]
                    if options and all(isinstance(opt, str) for opt in options):
                        new_args[options_index] = [translate_if_needed(opt, is_widget=True) for opt in options]
                elif "options" in kwargs:
                    options = kwargs["options"]
                    if options and all(isinstance(opt, str) for opt in options):
                        kwargs["options"] = [translate_if_needed(opt, is_widget=True) for opt in options]
                        
        return orig_method(self, *new_args, **kwargs)
        
    setattr(DeltaGenerator, method_name, wrapper)

def patch_write():
    """Patches DeltaGenerator.write to handle multiple string values."""
    orig_write = getattr(DeltaGenerator, "write", None)
    if not orig_write:
        return
        
    @functools.wraps(orig_write)
    def wrapper(self, *args, **kwargs):
        target_lang = st.session_state.get("language", "English")
        if target_lang == "English":
            return orig_write(self, *args, **kwargs)
            
        new_args = []
        for arg in args:
            if isinstance(arg, str):
                new_args.append(translate_if_needed(arg))
            else:
                new_args.append(arg)
        return orig_write(self, *new_args, **kwargs)
        
    setattr(DeltaGenerator, "write", wrapper)

def patch_page_and_navigation():
    """Patches streamlit.Page and streamlit.navigation to localize sidebar and routing titles."""
    orig_Page = getattr(st, "Page", None)
    if orig_Page:
        @functools.wraps(orig_Page)
        def custom_Page(page, *args, **kwargs):
            target_lang = st.session_state.get("language", "English")
            if target_lang != "English":
                title = kwargs.get("title")
                if title:
                    kwargs["title"] = translate_if_needed(title, is_widget=True)
                elif len(args) > 0:
                    args_list = list(args)
                    args_list[0] = translate_if_needed(args_list[0], is_widget=True)
                    args = tuple(args_list)
            return orig_Page(page, *args, **kwargs)
        st.Page = custom_Page
        
    orig_navigation = getattr(st, "navigation", None)
    if orig_navigation:
        @functools.wraps(orig_navigation)
        def custom_navigation(pages, *args, **kwargs):
            target_lang = st.session_state.get("language", "English")
            if target_lang != "English":
                if isinstance(pages, dict):
                    translated_pages = {}
                    for section, page_list in pages.items():
                        translated_section = translate_if_needed(section, is_widget=True)
                        translated_pages[translated_section] = page_list
                    pages = translated_pages
            return orig_navigation(pages, *args, **kwargs)
        st.navigation = custom_navigation

def patch_ui_components():
    """Patches the custom components module components.ui directly."""
    try:
        import components.ui as ui
        
        if hasattr(ui, "render_header"):
            orig_render_header = ui.render_header
            @functools.wraps(orig_render_header)
            def custom_render_header(title, subtitle=None):
                title = translate_if_needed(title)
                if subtitle:
                    subtitle = translate_if_needed(subtitle)
                return orig_render_header(title, subtitle)
            ui.render_header = custom_render_header
            
        if hasattr(ui, "render_metric"):
            orig_render_metric = ui.render_metric
            @functools.wraps(orig_render_metric)
            def custom_render_metric(label, value, trend=None, trend_color="success"):
                label = translate_if_needed(label)
                value = translate_if_needed(value)
                if trend:
                    trend = translate_if_needed(trend)
                return orig_render_metric(label, value, trend, trend_color)
            ui.render_metric = custom_render_metric
            
        if hasattr(ui, "render_toast"):
            orig_render_toast = ui.render_toast
            @functools.wraps(orig_render_toast)
            def custom_render_toast(message, icon="ℹ️"):
                message = translate_if_needed(message, is_widget=True)
                return orig_render_toast(message, icon)
            ui.render_toast = custom_render_toast
            
        if hasattr(ui, "show_loading_skeleton"):
            orig_show_loading_skeleton = ui.show_loading_skeleton
            @functools.wraps(orig_show_loading_skeleton)
            def custom_show_loading_skeleton(seconds=1.0, message="Loading data..."):
                message = translate_if_needed(message, is_widget=True)
                return orig_show_loading_skeleton(seconds, message)
            ui.show_loading_skeleton = custom_show_loading_skeleton
            
    except Exception:
        pass

def initialize_translation():
    """Installs all language translation monkeypatches."""
    patch_delta_generator_method("markdown", arg_index=0, is_kwarg="body")
    patch_delta_generator_method("title", arg_index=0, is_kwarg="body")
    patch_delta_generator_method("header", arg_index=0, is_kwarg="body")
    patch_delta_generator_method("subheader", arg_index=0, is_kwarg="body")
    patch_delta_generator_method("caption", arg_index=0, is_kwarg="body")
    patch_delta_generator_method("text", arg_index=0, is_kwarg="body")
    
    # Notifications/Toasts (not widgets, but treated as static labels)
    patch_delta_generator_method("info", arg_index=0, is_kwarg="body", is_widget=True)
    patch_delta_generator_method("success", arg_index=0, is_kwarg="body", is_widget=True)
    patch_delta_generator_method("warning", arg_index=0, is_kwarg="body", is_widget=True)
    patch_delta_generator_method("error", arg_index=0, is_kwarg="body", is_widget=True)
    patch_delta_generator_method("toast", arg_index=0, is_kwarg="body", is_widget=True)
    
    # Active Interactive Widgets (marked with is_widget=True)
    patch_delta_generator_method("button", arg_index=0, is_kwarg="label", is_widget=True)
    patch_delta_generator_method("checkbox", arg_index=0, is_kwarg="label", is_widget=True)
    patch_delta_generator_method("toggle", arg_index=0, is_kwarg="label", is_widget=True)
    patch_delta_generator_method("text_input", arg_index=0, is_kwarg="label", is_widget=True)
    patch_delta_generator_method("text_area", arg_index=0, is_kwarg="label", is_widget=True)
    patch_delta_generator_method("chat_input", arg_index=0, is_kwarg="placeholder", is_widget=True)
    
    patch_delta_generator_method("radio", arg_index=0, is_kwarg="label", has_options=True, is_widget=True)
    patch_delta_generator_method("selectbox", arg_index=0, is_kwarg="label", has_options=True, is_widget=True)
    
    patch_write()
    patch_page_and_navigation()
    patch_ui_components()
