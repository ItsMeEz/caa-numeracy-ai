import json
import os
import time
import streamlit as st
from google import genai
from google.genai import types

# Page setup for clean embedding in Google Sites
st.set_page_config(page_title="CAA Quest: 30-Min Mastery", layout="wide")

# Read API key securely from Streamlit Secrets
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# ----------------- SESSION PERSISTENCE & ADAPTIVE TRACKING -----------------
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "solved" not in st.session_state:
    st.session_state.solved = 0
if "struggling_topics" not in st.session_state:
    st.session_state.struggling_topics = []
if "mistake_history" not in st.session_state:
    st.session_state.mistake_history = []
if "scenario" not in st.session_state:
    st.session_state.scenario = None
if "hint_level" not in st.session_state:
    st.session_state.hint_level = 0
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

# ----------------- LESSON FLASHCARDS -----------------
LESSONS = {
    "Percentages & Traps": """
    **⚡ Quick Flashcard:**
    * **Discounts:** $\\text{Percent Off} = (\\text{Saving} \\div \\text{Original}) \\times 100$.
    * **The Trap:** Buy 1 get 2nd half-price = **25% saving on total, NEVER 50%!**
    """,
    "Speed, Distance & Time": """
    **⚡ Quick Flashcard:**
    * $\\text{Distance} = \\text{Speed} \\times \\text{Time}$ | $\\text{Speed} = \\text{Distance} \\div \\text{Time}$
    * $\\text{km/h to m/min:} \\times 1,000 \\text{ then } \\div 60$.
    * **Decimal Time Trap:** $2.5\\text{ hrs} = 150\\text{ mins}$ (Base 60, not 2 hrs 50 mins!).
    """,
    "Mass & Capacity (kg/g, L/mL)": """
    **⚡ Quick Flashcard:**
    * $1\\text{ kg} = 1,000\\text{ g}$ | $1\\text{ Litre} = 1,000\\text{ mL}$
    * $\\text{Price per kg:} \\text{Cost} = (\\text{Grams} \\div 1,000) \\times \\text{Price/kg}$.
    """,
    "Agree / Disagree Evidence (Outcome 3)": """
    **⚡ Quick Flashcard:**
    * **Rule 1:** State your stance clearly (Agree, Disagree, or Unsure).
    * **Rule 2:** You MUST quote at least two exact numbers or percentages from the problem.
    """,
}

# ----------------- ADAPTIVE AI ENGINE -----------------
SYSTEM_PROMPT = """
You are an adaptive AI examiner for the NCEA Numeracy CAA (Unit Standard 32406).
Your goal is to gamify math for learners with short attention spans.

TOPICS TO CYCLE THROUGH:
1. Mass & Unit Rates ($/kg, kg <-> g, meat budgets)
2. Speed, Distance & Time (km/h to m/min, decimal time traps like 2.5 hrs = 150 min)
3. Capacity & Volumes (serving 27 people with multiple bottle sizes)
4. Outcome 3 Claims (Agree/Disagree statements with tables or graph frequencies)

CRITICAL INSTRUCTIONS:
- Adaptability: If the learner struggled with previous topics, explicitly generate a problem on that concept with fresh numbers.
- Math Symbols: Always format arithmetic with "×" and "÷". NEVER use "*" or "/".
- Style: Punchy, high-energy, direct language.

OUTPUT FORMAT:
Return strictly a valid JSON object with no markdown fences, backticks, or extra commentary:
{
  "topic": "Topic Name",
  "is_targeted_weakness": true,
  "requires_working": false,
  "scenario_data": "Short table, numbers, or frequency context",
  "question": "Clear, engaging problem text",
  "plain_english": "1-sentence plain-English translation of what to do",
  "expected_answer": "Target answer or criteria",
  "hint_1": "Step 1: Formula or initial conversion",
  "hint_2": "Step 2: Arithmetic setup with × or ÷",
  "solution": "Full working showing step-by-step arithmetic with × and ÷"
}
"""


def generate_adaptive_problem():
    weaknesses_str = (
        ", ".join(st.session_state.struggling_topics[-3:])
        if st.session_state.struggling_topics
        else "None yet"
    )

    user_prompt = f"""
    The learner's current weak areas needing repetition: [{weaknesses_str}].
    Recent errors: {st.session_state.mistake_history[-2:] if st.session_state.mistake_history else 'None'}.
    
    If weak areas exist, generate a targeted remediation problem on that skill with new numbers.
    Otherwise, choose a high-frequency CAA question from the topics list.
    Vary 'requires_working' (True for claims/equations, False for quick calculations).
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=user_prompt,
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


# ----------------- UI / GAMIFICATION BAR -----------------
# 30-Minute Run Timer calculation
elapsed_mins = int((time.time() - st.session_state.start_time) / 60)
mins_left = max(0, 30 - elapsed_mins)

st.markdown("## ⚡ NCEA CAA: Speed-Run Arena")

# HUD Bar
hcol1, hcol2, hcol3, hcol4, hcol5 = st.columns(5)
with hcol1:
    st.metric("⏳ 30-Min Run", f"{mins_left}m left")
with hcol2:
    st.metric("⭐ XP Points", st.session_state.xp)
with hcol3:
    st.metric("🔥 Combo Streak", f"{st.session_state.streak}x")
with hcol4:
    st.metric("🎯 Problems Solved", st.session_state.solved)
with hcol5:
    level = (
        "👑 Boss"
        if st.session_state.xp >= 300
        else (
            "🥇 Pro"
            if st.session_state.xp >= 150
            else (
                "🥈 Apprentice" if st.session_state.xp >= 60 else "🥉 Cadet"
            )
        )
    )
    st.metric("🎖️ Rank", level)

# Weakness radar tracker
if st.session_state.struggling_topics:
    st.info(
        f"🎯 **AI Adaptation Radar:** Active drills queued for: **{', '.join(set(st.session_state.struggling_topics))}**"
    )

# Lesson Flashcards Accordion
with st.expander("⚡ 10-Second Formula Flashcards (Click to Open)"):
    tab1, tab2, tab3, tab4 = st.tabs(list(LESSONS.keys()))
    for tab, (name, content) in zip([tab1, tab2, tab3, tab4], LESSONS.items()):
        with tab:
            st.markdown(content)

st.divider()

# ----------------- MAIN STAGE -----------------
col_main, col_guide = st.columns([1.3, 1])

with col_main:
    if st.button("🚀 Spawn Next Challenge") or st.session_state.scenario is None:
        generate_adaptive_problem()

    sc = st.session_state.scenario
    if sc:
        if sc.get("is_targeted_weakness"):
            st.warning("🔁 **Adaptive Rematch:** Re-targeting a past mistake!")

        st.caption(f"**Focus Strand:** {sc.get('topic', 'CAA Practice')}")

        if sc.get("scenario_data"):
            st.info(f"📊 **Data Stimulus:**\n{sc.get('scenario_data')}")

        st.markdown(f"### {sc.get('question')}")
        st.markdown(
            f"💡 **In Plain English:** {sc.get('plain_english', '')}"
        )

        needs_working = sc.get("requires_working", False)
        if needs_working:
            st.markdown("✍️ **Show Your Equations or Verdict with Numbers:**")
            user_input = st.text_area(
                "Your Working:",
                key="ans_area",
                placeholder="Write your equations or state agree/disagree with numbers...",
                height=100,
            )
        else:
            st.markdown("⚡ **Quick Strike Answer:**")
            user_input = st.text_input(
                "Your Answer:",
                key="ans_input",
                placeholder="Enter value (e.g. 250 m, $6.80, or 45)",
            )

        if st.button("🎯 Submit Answer") and user_input:
            eval_prompt = f"""
            Scenario Data: {sc.get('scenario_data')}
            Question: {sc.get('question')}
            Topic: {sc.get('topic')}
            Requires Full Working: {needs_working}
            Target Answer: {sc.get('expected_answer')}
            Student Input: {user_input}

            Output strictly JSON:
            {{
               "is_correct": true/false,
               "verdict": "Punchy 1-sentence assessment",
               "working": "Clear step-by-step arithmetic using '×' and '÷'"
            }}
            """
            eval_res = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=eval_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            res_data = json.loads(eval_res.text)
            st.session_state.feedback = res_data

            if res_data.get("is_correct"):
                st.session_state.streak += 1
                gain = 25 + (st.session_state.streak * 5)
                st.session_state.xp += gain
                st.session_state.solved += 1

                # Clear mastered topic from weak list
                topic = sc.get("topic")
                if topic in st.session_state.struggling_topics:
                    st.session_state.struggling_topics.remove(topic)

                if st.session_state.streak % 3 == 0:
                    st.balloons()
            else:
                st.session_state.streak = 0
                topic = sc.get("topic")
                if topic:
                    st.session_state.struggling_topics.append(topic)
                st.session_state.mistake_history.append(
                    f"{topic}: Student wrote '{user_input}'"
                )

        if st.session_state.feedback:
            fb = st.session_state.feedback
            if fb.get("is_correct"):
                st.success(
                    f"🎉 **{fb.get('verdict')}**\n\n{fb.get('working')}"
                )
            else:
                st.error(
                    f"❌ **{fb.get('verdict')}**\n\n**Correct Working:**\n{fb.get('working')}"
                )

with col_guide:
    st.markdown("### 🤖 Instant AI Copilot")
    if sc:
        if st.session_state.hint_level >= 1:
            st.warning(f"**Step 1:** {sc.get('hint_1')}")
        if st.session_state.hint_level >= 2:
            st.warning(f"**Step 2:** {sc.get('hint_2')}")
        if st.session_state.hint_level >= 3:
            st.success(f"**Solution:** {sc.get('solution')}")

        if st.session_state.hint_level < 3:
            if st.button("💡 Grab a Hint (No penalty)"):
                st.session_state.hint_level += 1
                st.rerun()
