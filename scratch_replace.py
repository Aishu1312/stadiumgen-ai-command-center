import os
import glob

views_dir = r"c:\Users\Aishwarya Lala\Downloads\PromptWars(Challenge 4)\views"
files = glob.glob(os.path.join(views_dir, "*.py"))

for file_path in files:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Replace the error strings
    content = content.replace('st.error(f"🚨 Error: {e}")', 'st.warning(str(e))')
    content = content.replace('st.error("🚨 Error: An unexpected error occurred.")', 'st.error("An unexpected error occurred. Please try again later.")')
    
    # Also replace spinners if we want to change them later, but let's stick to the prompt's request.
    # The prompt asks for:
    # Connecting to AI...
    # Processing your request...
    # Optimizing response...
    # Finalizing answer...
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
print("Replacements done.")
