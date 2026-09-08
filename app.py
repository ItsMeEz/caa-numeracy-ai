import json
import os
import streamlit as st
from google import genai
from google.genai import types

# Page setup for clean embedding in Google Sites
st.set_page_config(page_title="NCEA CAA Numeracy Master", layout="wide")

# Read API key securely from Streamlit Secrets
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
You are an expert NCEA Numeracy examiner creating authentic Level 4/5 questions for New Zealand Unit Standard 32406.
Your questions must NOT be overly simple. They must cycle randomly through these 4 CAA categories:

1. MASS & RATE CALCULATIONS (kg and g):
   - Supermarket weights, e.g., buying 760 g of fruit at $8.95/kg, or finding the average weight in grams of 1 kiwifruit if 10 weigh 1.2 kg.
   - Gas usage, e.g., 4 burners using 150 g/hour over 2.5 hours.

2. CAPACITY & BENCHMARKS (Litres and mL):
   - Multi-bottle calculations, e.g., 2x 3L juice + 1x 5L water + 4x 2.25L drinks. Will this serve 27 people drinking 750 mL each?

3. TIME CONVERSIONS & SPEED:
   - Converting km/h to metres per minute (e.g., 15 km/h = 15,000 m/hr ÷ 60 = 250 m/min).
   - Decimal time traps (e.g., explaining why 2.5 hours is 150 minutes, NOT 2 hours 50 minutes).

4. GRAPH INTERPRETATION & AGREE / DISAGREE CLAIMS (Outcome 3):
   - Provide a clear data scenario or frequency distribution (e.g., 100 skateboards tested: 41 broke under 9 months, 59 lasted 9+ months).
   - State a claim: "The maker claims more than half lasted 9 months or more. Do you agree or disagree? Explain using numbers."
   - Retail claims: "Buy one pair, get second pair half price means you save 50% on the total. Agree or disagree?"

MATHEMATICAL FORMATTING RULES:
- Always use standard school symbols: "×" for multiplication and "÷" for division. NEVER use "*" or "/".
- Provide clear, supportive, plain English language.

OUTPUT FORMAT:
Return strictly a valid JSON object with no markdown fences, backticks, or extra text:
{
  "category": "One of: Mass (kg/g) | Capacity (L/mL) | Time & Speed | Graph & Claim (Agree/Disagree)",
  "scenario_data": "If a graph, table, or context is needed, describe the data values clearly here.",
  "question": "The specific question the student must answer.",
  "plain_english": "A 1-2 sentence plain-language translation of what the student needs to calculate or evaluate.",
  "expected_answer": "The target numerical answer or required verdict (e.g. 'Disagree, savings is 25%', '250 m', '$6.80')",
  "hint_1": "Step 1: Formula or initial conversion to set up (using × or ÷)",
  "hint_2": "Step 2: Intermediate calculation",
  "solution": "Full working showing step-by-step arithmetic using × and ÷"
}
"""

# Initialize session state
if "scenario" not in st.session_state:
    st.session_state.scenario = None
if "hint_level" not in st.session_state:
    st.session_state.hint_level = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "feedback" not in st.session_state:
    st.session_state.feedback = None


def generate_new_problem():
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents="Generate a challenging, authentic CAA Numeracy question across mass, capacity, speed-time, or agree/disagree graph claims.",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
            ),
        )
        st.session_state.scenario = json.loads(response.text)
        st.session_state.hint_level = 0
        st.session_state.feedback = None
    except Exception as e:
        st.error(f"Error connecting to Gemini: {e}")


# App Interface
st.markdown("## 📊 NCEA Numeracy CAA: Advanced Practice Engine")

col1, col2 = st.columns([1.3, 1])

with col1:
    if st.button("🔄 Generate New Question") or st.session_state.scenario is None:
        generate_new_problem()

    sc = st.session_state.scenario
    if sc:
        st.caption(f"**Focus Strand:** {sc.get('category', 'Numeracy')}")

        # If there is data/graph context, show it in a highlighted box
        if sc.get("scenario_data"):
            st.info(f"📋 **Context / Data:**\n{sc.get('scenario_data')}")

        st.markdown(f"### {sc.get('question')}")
        st.markdown(
            f"💡 **In Plain English:** {sc.get('plain_english', '')}"
        )

        user_input = st.text_area(
            "Your Working & Answer (Type your answer, or Agree/Disagree with your reason):",
            key="user_ans",
            placeholder="e.g., 250 m OR I disagree because...",
            height=100,
        )

        if st.button("Check Answer") and user_input:
            verify_prompt = f"""
            Scenario Data: {sc.get('scenario_data')}
            Question: {sc.get('question')}
            Expected Target / Criteria: {sc.get('expected_answer')}
            Student Response: {user_input}

            Evaluate the student's submission based on NCEA CAA requirements:
            1. Did they get the calculation right (with reasonable rounding)?
            2. If it is an Agree/Disagree question, did they state an agreeable stance AND support it with numerical evidence?
            3. Use '×' for times and '÷' for divide in all mathematical working. Never use '*' or '/'.
            
            Give an encouraging 1-sentence verdict, then display the step-by-step arithmetic solution.
            """
            eval_res = client.models.generate_content(
                model="gemini-3.6-flash", contents=verify_prompt
            )
            st.session_state.feedback = eval_res.text

        if st.session_state.feedback:
            st.success(st.session_state.feedback)

with col2:
    st.markdown("### 🤖 Step-by-Step AI Guide")
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
