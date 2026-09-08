import json
import os
import time
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="CAA Quest: 30-Min Mastery", layout="wide")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# ----------------- SESSION PERSISTENCE -----------------
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
if "next_prefetched_scenario" not in st.session_state:
    st.session_state.next_prefetched_scenario = None
if "hint_level" not in st.session_state:
    st.session_state.hint_level = 0
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": "Kia ora! I am your CAA Numeracy Coach. Ask me how to calculate anything, or ask me to explain a step!",
        }
    ]

# ----------------- FLASHCARDS -----------------
LESSONS = {
    "Percentages & Traps": """
    ### 📓 COPY INTO YOUR NOTEBOOK:
    * **Finding Percentage Discount:** **Percent Off = (Discount ÷ Original Price) × 100**[cite: 1, 2, 3]
    * **15% GST Rule:** **Total Price = Price × 1.15** (or **Price + [Price × 0.15]**)
    * **The Two-Pair Trap:** Buy one pair, get 2nd half price = **You save 25% on the total purchase, NOT 50%!**[cite: 2, 3]
    """,
    "Speed, Distance & Time": """
    ### 📓 COPY INTO YOUR NOTEBOOK:
    * **Distance Equation:** **Distance = Speed × Time**
    * **Speed Equation:** **Speed = Distance ÷ Time**
    * **Time Equation:** **Time = Distance ÷ Speed**
    * **Speed Conversion:** **Metres per min = (Speed in km/h × 1,000) ÷ 60**[cite: 1, 2, 3]
    * **Base-60 Time Trap:** Time is NOT out of 100!
      * **2.5 hours = 2 hours and 30 minutes = 150 minutes** (NEVER 2 hours 50 minutes!)[cite: 1]
      * **2.25 hours = 2 hours and 15 minutes = 135 minutes**
    """,
    "Mass & Capacity (kg, g, L, mL)": """
    ### 📓 COPY INTO YOUR NOTEBOOK:
    * **Mass Conversion:** **1 kg = 1,000 g**
      * **kg to g:** Multiply by 1,000 (**kg × 1,000 = g**)
      * **g to kg:** Divide by 1,000 (**g ÷ 1,000 = kg**)
    * **Price Per Kilogram:** **Cost = (Grams ÷ 1,000) × Price per kg**[cite: 1, 2, 3]
    * **Capacity Conversion:** **1 Litre = 1,000 mL**[cite: 1, 2, 3]
    * **Liquid Servings:** **Total Litres Needed = (People × mL per person) ÷ 1,000**[cite: 1, 2, 3]
    """,
    "Outcome 3 Claims (Agree/Disagree)": """
    ### 📓 COPY INTO YOUR NOTEBOOK:
    * **Rule 1 (Position):** Start with **"I agree"** or **"I disagree"**[cite: 2, 3].
    * **Rule 2 (Numerical Proof):** Quote at least **two exact numbers, frequencies, or percentages** from the data[cite: 1, 2, 3].
    * **Rule 3 (Comparison):** Show the math comparison (e.g., **"59 out of 100 is 59%, which is greater than half (50%)"**)[cite: 2, 3].
    """,
}

# ----------------- SYSTEM PROMPT -----------------
SYSTEM_PROMPT = """
You are an adaptive AI examiner for the NCEA Numeracy CAA (Unit Standard 32406).
Generate authentic Level 4/5 questions matching the 2026 examination paper.

IMPORTANT INSTRUCTIONS:
1. EQUATION FORMATTING:
   - EVERY equation, arithmetic formula, and calculation MUST BE IN BOLD (e.g. **15 × 1,000 = 15,000**, **15,000 ÷ 60 = 250 m**).
   - Use standard school symbols: "×" for multiplication and "÷" for division. NEVER use "*" or "/".
2. STRICT NUMERICAL TARGET:
   - Always provide an exact clean numeric string or short value in "clean_numeric_target" (e.g. "250", "6.80", "14", "120") if requires_working is false.
3. NOTEBOOK HIGHLIGHT:
   - Include a punchy "notebook_rule" with the bold formula the learner must record.

OUTPUT FORMAT:
Return strictly a valid JSON object with no markdown fences, backticks, or extra commentary:
{
  "topic": "Topic Name",
  "is_targeted_weakness": false,
  "requires_working": false,
  "clean_numeric_target": "250",
  "scenario_data": "Short table or context numbers",
  "question": "Clear problem text",
  "plain_english": "1-sentence plain-English breakdown",
  "notebook_rule": "**Metres per min = (km/h × 1,000) ÷ 60**",
  "expected_answer": "Target answer or criteria",
  "hint_1": "Step 1: Formula with bold equations",
  "hint_2": "Step 2: Arithmetic setup with bold equations",
  "solution": "Full working showing step-by-step arithmetic in BOLD using × and ÷"
}
"""

def request_gemini_question():
    weaknesses_str = ", ".join(st.session_state.struggling_topics[-3:]) if st.session_state.struggling_topics else "None"
    user_prompt = f"""
    Learner weak areas: [{weaknesses_str}].
    Recent errors: {st.session_state.mistake_history[-2:] if st.session_state.mistake_history else 'None'}.
    Generate one fresh CAA question. Keep equations bolded with '×' and '÷'.
    """
    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            if attempt == 1:
                st.warning("⚠️ High server traffic. Retrying smoothly...")
            time.sleep(1)
    return None

def spawn_question():
    # Use prefetched question if available for instant load
    if st.session_state.next_prefetched_scenario:
        st.session_state.scenario = st.session_state.next_prefetched_scenario
        st.session_state.next_prefetched_scenario = None
    else:
        st.session_state.scenario = request_gemini_question()
    
    st.session_state.hint_level = 0
    st.session_state.feedback = None

# Pre-fetch the initial question
if st.session_state.scenario is None:
    spawn_question()

# ----------------- UI / GAMIFICATION HUD -----------------
elapsed_mins = int((time.time() - st.session_state.start_time) / 60)
mins_left = max(0, 30 - elapsed_mins)

st.markdown("## ⚡ NCEA CAA: Speed-Run Arena")

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
    level = "👑 Boss" if st.session_state.xp >= 300 else ("🥇 Pro" if st.session_state.xp >= 150 else ("🥈 Apprentice" if st.session_state.xp >= 60 else "🥉 Cadet"))
    st.metric("🎖️ Rank", level)

if st.session_state.struggling_topics:
    st.info(f"🎯 **AI Adaptation Radar:** Targeting past errors: **{', '.join(set(st.session_state.struggling_topics))}**")

with st.expander("📓 View Notebook Formula Sheets (Click to Open)"):
    tab1, tab2, tab3, tab4 = st.tabs(list(LESSONS.keys()))
    for tab, (name, content) in zip([tab1, tab2, tab3, tab4], LESSONS.items()):
        with tab:
            st.markdown(content)

st.divider()

# ----------------- MAIN ARENA -----------------
col_main, col_chat = st.columns([1.3, 1])

with col_main:
    if st.button("🚀 Spawn Next Challenge"):
        spawn_question()
        st.rerun()

    sc = st.session_state.scenario
    if sc:
        if sc.get("is_targeted_weakness"):
            st.warning("🔁 **Adaptive Rematch:** Re-targeting your past mistake!")

        st.caption(f"**Focus Strand:** {sc.get('topic', 'CAA Practice')}")

        if sc.get("notebook_rule"):
            st.markdown(
                f"""
                <div style="background: rgba(251, 191, 36, 0.15); border: 2px dashed #fbbf24; border-radius: 8px; padding: 10px; margin-bottom: 12px;">
                    <span style="font-weight: 800; color: #fbbf24;">📓 WRITE THIS IN YOUR NOTEBOOK:</span><br>
                    <span style="font-size: 1.05rem; color: #fff;">{sc.get('notebook_rule')}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        if sc.get("scenario_data"):
            st.info(f"📊 **Data Context:**\n{sc.get('scenario_data')}")

        st.markdown(f"### {sc.get('question')}")
        st.markdown(f"💡 **In Plain English:** {sc.get('plain_english', '')}")

        needs_working = sc.get("requires_working", False)
        if needs_working:
            st.markdown("✍️ **Show Your Equations or Verdict with Numbers:**")
            user_input = st.text_area(
                "Your Working:",
                key="ans_area",
                placeholder="Write your equations or state agree/disagree with numbers...",
                height=90
            )
        else:
            st.markdown("⚡ **Quick Strike Answer:**")
            user_input = st.text_input(
                "Your Answer:",
                key="ans_input",
                placeholder="Enter value (e.g. 250 m, $6.80, or 45)"
            )

        if st.button("🎯 Submit Answer") and user_input:
            # INSTANT VERIFICATION FOR NUMERIC ANSWERS (No API lag)
            clean_target = str(sc.get("clean_numeric_target", "")).strip().lower()
            clean_user = "".join(c for c in user_input if c.isalnum() or c == ".").lower()

            if not needs_working and clean_target and (clean_target in clean_user or clean_user in clean_target):
                # Instant local verification in 0.01 seconds
                res_data = {
                    "is_correct": True,
                    "verdict": "Fast and Accurate!",
                    "working": sc.get("solution", "")
                }
            else:
                # LLM check for open-ended Outcome 3 claims or nuanced formats
                eval_prompt = f"""
                Scenario Data: {sc.get('scenario_data')}
                Question: {sc.get('question')}
                Requires Full Working: {needs_working}
                Target Answer: {sc.get('expected_answer')}
                Student Input: {user_input}

                Output strictly JSON:
                {{
                   "is_correct": true/false,
                   "verdict": "Punchy 1-sentence assessment",
                   "working": "Clear step-by-step arithmetic with ALL EQUATIONS IN BOLD using '×' and '÷'"
                }}
                """
                try:
                    eval_res = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=eval_prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json"),
                    )
                    res_data = json.loads(eval_res.text)
                except Exception:
                    res_data = {
                        "is_correct": False,
                        "verdict": "Answer submitted. Check working below:",
                        "working": sc.get("solution", "")
                    }

            st.session_state.feedback = res_data

            if res_data.get("is_correct"):
                st.session_state.streak += 1
                gain = 25 + (st.session_state.streak * 5)
                st.session_state.xp += gain
                st.session_state.solved += 1

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
                st.session_state.mistake_history.append(f"{topic}: Student wrote '{user_input}'")

        if st.session_state.feedback:
            fb = st.session_state.feedback
            if fb.get("is_correct"):
                st.success(f"🎉 **{fb.get('verdict')}**\n\n{fb.get('working')}")
            else:
                st.error(f"❌ **{fb.get('verdict')}**\n\n**Correct Equations & Working:**\n{fb.get('working')}")

        with st.expander("💡 Need Step-by-Step Help? (No penalty)"):
            if st.session_state.hint_level >= 1:
                st.warning(f"**Step 1:** {sc.get('hint_1')}")
            if st.session_state.hint_level >= 2:
                st.warning(f"**Step 2:** {sc.get('hint_2')}")
            if st.session_state.hint_level >= 3:
                st.success(f"**Full Working:** {sc.get('solution')}")

            if st.session_state.hint_level < 3:
                if st.button("Unlock Next Step"):
                    st.session_state.hint_level += 1
                    st.rerun()

# ----------------- AI CHATBOT COPILOT -----------------
with col_chat:
    st.markdown("### 💬 Ask AI Coach")
    st.caption("Ask questions about equations, formulas, or how to solve steps!")

    chat_box = st.container(height=400)
    for msg in st.session_state.chat_messages:
        with chat_box.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_query = st.chat_input("Ask: e.g. How do I turn km/h into m/min?")
    if user_query:
        st.session_state.chat_messages.append({"role": "user", "content": user_query})
        with chat_box.chat_message("user"):
            st.markdown(user_query)

        current_q_context = f"The current problem is: {sc.get('question')} | Data: {sc.get('scenario_data')}" if sc else "General practice"
        tutor_prompt = f"""
        You are an encouraging NCEA Numeracy tutor for students with low attention spans.
        Context: {current_q_context}.
        Student Question: {user_query}
        RULES: Format ALL equations in **BOLD**. Always use '×' and '÷'. Keep answers short (under 3 bullets).
        """
        try:
            bot_res = client.models.generate_content(
                model="gemini-3.6-flash", contents=tutor_prompt
            )
            reply = bot_res.text
        except Exception:
            reply = "I am catching my breath! Try that question once more in 5 seconds."

        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        with chat_box.chat_message("assistant"):
            st.markdown(reply)
