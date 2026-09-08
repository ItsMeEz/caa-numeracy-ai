import json
import os
import streamlit as st
from google import genai
from google.genai import types

# Page setup for clean embedding in Google Sites
st.set_page_config(page_title="CAA Numeracy AI Tutor", layout="wide")

# Read API key securely from Streamlit Secrets
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
You are an expert NCEA Numeracy tutor for New Zealand Unit Standard 32406.
Your job is to generate authentic Level 4/5 everyday math problems matching the 2026 CAA paper:
- Real NZ contexts: Supermarket shopping ($/kg), gas cooker usage rates, running shoe lifespans, scale drawings, and time conversions (hours to minutes).
- Mathematical Symbols Rule: Always format arithmetic clearly for school students. Use the standard multiplication sign "×" (or "times") instead of "*". Use the standard division sign "÷" (or "divided by") instead of "/".
- Plain English: Write in direct, welcoming English that struggling readers can understand immediately.
- JSON Output: You must always output valid JSON with no markdown wrapping or code blocks.

Format:
{
  "topic": "Context name (e.g. Supermarket Budget)",
  "question": "Clear problem statement with all given values.",
  "plain_english": "A 1-sentence plain translation of what to do.",
  "expected_answer": "The numerical answer or short unit string (e.g. 14 bees, $25, or 250 m)",
  "hint_1": "Step 1: Identify the numbers and formula needed",
  "hint_2": "Step 2: Show the setup calculation with × or ÷",
  "solution": "Step 3: Full worked solution with complete arithmetic using × and ÷"
}
"""

# Initialize session states
if "scenario" not in st.session_state:
    st.session_state.scenario = None
if "hint_level" not in st.session_state:
    st.session_state.hint_level = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "verified" not in st.session_state:
    st.session_state.verified = False


def generate_new_problem():
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Generate a new randomized CAA Numeracy question.",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
            ),
        )
        st.session_state.scenario = json.loads(response.text)
        st.session_state.hint_level = 0
        st.session_state.verified = False
    except Exception as e:
        st.error(f"Error connecting to Gemini: {e}")


# App Layout
st.markdown("## 📐 NCEA Numeracy CAA: AI Practice Engine")

col1, col2 = st.columns([1.2, 1])

with col1:
    if st.button("🔄 Generate New Question") or st.session_state.scenario is None:
        generate_new_problem()

    sc = st.session_state.scenario
    if sc:
        st.caption(f"**Standard Strand:** {sc.get('topic', 'General Numeracy')}")
        st.info(sc.get("question", ""))
        st.markdown(
            f"💡 **In Plain English:** {sc.get('plain_english', '')}"
        )

        user_input = st.text_input(
            "Your Answer:", key="user_ans", placeholder="Type your answer here..."
        )

        if st.button("Check Answer") and user_input:
            st.session_state.verified = True
            verify_prompt = f"""
            Question: {sc.get('question')}
            Target Answer: {sc.get('expected_answer')}
            Student Answer: {user_input}

            Evaluate if the student is mathematically correct or within reasonable rounding tolerance.
            Important: In all arithmetic working, use standard school symbols: "×" for multiplication and "÷" for division. Never use programming symbols like "*" or "/".
            Be encouraging. Output a 1-sentence verdict followed by the step-by-step calculation.
            """
            eval_res = client.models.generate_content(
                model="gemini-2.5-flash", contents=verify_prompt
            )
            st.success(eval_res.text)

with col2:
    st.markdown("### 🤖 AI Step-by-Step Guide")
    if sc:
        if st.session_state.hint_level >= 1:
            st.warning(f"**Step 1:** {sc.get('hint_1')}")
        if st.session_state.hint_level >= 2:
            st.warning(f"**Step 2:** {sc.get('hint_2')}")
        if st.session_state.hint_level >= 3:
            st.success(f"**Full Working:** {sc.get('solution')}")

        if st.session_state.hint_level < 3:
            if st.button("💡 Need a Hint?"):
                st.session_state.hint_level += 1
                st.rerun()
