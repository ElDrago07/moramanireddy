import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyBT9R60jk43uMuXA4Tox8538RcrCOswtn0"

import requests
import google.generativeai as genai
from bs4 import BeautifulSoup

# -----------------------------
# CONFIGURATION
# -----------------------------
WEBPAGE_URL = "https://www.bbc.com/news/technology"   # choose any from the list
OUTPUT_FILE = "summary_output.txt"

# -----------------------------
# 1. FETCH WEBPAGE
# -----------------------------
def fetch_webpage(url: str) -> str:
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return resp.text

# -----------------------------
# 2. CLEAN HTML
# -----------------------------
def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Remove scripts, styles, nav, footer, etc.
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    # Condense whitespace
    text = " ".join(text.split())
    return text[:15000]   # limit size for model

# -----------------------------
# 3. CONNECT TO GEMINI 2.5 FLASH
# -----------------------------
def init_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("Please set GOOGLE_API_KEY in your environment.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    return model

# -----------------------------
# 4. CREATE PROMPT
# -----------------------------
def build_prompt(clean_text: str) -> str:
    prompt = f"""
You are an analytical technology journalist.
Analyze the following webpage content and summarize it into
3–5 concise bullet points focusing on the key technological,
ethical, or business implications discussed.

After the bullet points, write one short single-line *Insight*
that interprets what the overall theme or trend means for society
or the tech industry.

Return the answer strictly in this structure:
Summary:
• <point 1>
• <point 2>
• <point 3>
• <point 4>
• <point 5>
Insight:
<single-line insight>

Content to analyze:
\"\"\"{clean_text}\"\"\"
"""
    return prompt.strip()

# -----------------------------
# 5. ASK GEMINI & FORMAT RESULT
# -----------------------------
def analyze_with_gemini(model, prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text.strip()

# -----------------------------
# 6. SAVE + PRINT RESULT
# -----------------------------
def save_output(text: str):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)

# -----------------------------
# MAIN EXECUTION
# -----------------------------
def main():
    print(f"Fetching webpage: {WEBPAGE_URL}")
    html = fetch_webpage(WEBPAGE_URL)
    cleaned = clean_html(html)
    model = init_gemini()
    prompt = build_prompt(cleaned)
    print("Analyzing with Gemini 2.5 Flash ...")
    result = analyze_with_gemini(model, prompt)
    print("\n--- RESULT ---")
    save_output(result)
    print(f"\nSaved output to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
