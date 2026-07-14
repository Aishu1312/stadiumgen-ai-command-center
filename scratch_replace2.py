import os
import glob
import re

views_dir = r"c:\Users\Aishwarya Lala\Downloads\PromptWars(Challenge 4)\views"
files = glob.glob(os.path.join(views_dir, "*.py"))

for file_path in files:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    original = content
    
    # Check if file has st.spinner for AI (ignore generating audio)
    if 'st.spinner("Connecting to AI...")' in content or 'st.spinner("Generating response...")' in content:
        # Import ai_processing_status if not there
        if "from components.ui import ai_processing_status" not in content:
            if "from components.ui import" in content:
                content = re.sub(r'from components\.ui import (.+)', r'from components.ui import \1, ai_processing_status', content, count=1)
            else:
                # find a good place to inject
                content = content.replace("import streamlit as st", "import streamlit as st\nfrom components.ui import ai_processing_status")
                
        # Replace spinners
        content = content.replace('with st.spinner("Connecting to AI..."):', 'with ai_processing_status() as _status:\n                    _status.update(label="Processing your request...")')
        content = content.replace('with st.spinner("Generating response..."):', 'with ai_processing_status() as _status:\n                    _status.update(label="Processing your request...")')
        
        # fix indentation slightly if needed, but the original with st.spinner is usually indented, replacing it keeps the same indentation for the `with`, and then we add a new line and indent the _status.update relative to the new `with`.
        
    if content != original:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
print("Replacement done.")
