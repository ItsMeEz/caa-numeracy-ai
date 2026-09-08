import html
import json
import os
import random
import re
import time
import streamlit as st
from google import genai

# ---------------------------------------------------------
# PLATFORM CONFIGURATION & UNIVERSAL THEME LOCK
# ---------------------------------------------------------
st.set_page_config(
    page_title="Apex Numeracy | NCEA CAA Master",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Enforce high-contrast styles across both Light & Dark device themes
st.markdown(
    """
<style>
    @import url('[https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap](https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap)');
    
    :root {
        --text-headline: #ffffff !important;
        --text-sub: #cbd5e1 !important;
        --hud-bg: #0f172a !important;
        --card-border: #334155 !important;
        --gold-bright: #fbbf24 !important;
        --gold-bg: rgba(251, 191, 36, 0.16) !important;
        --blue-bright: #38bdf8 !important;
        --blue-bg: rgba(56, 189, 248, 0.12) !important;
    }

    * { 
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }

    .block-container { 
        padding-top: 1.2rem; 
        padding-bottom: 2rem; 
        max-width: 1250px; 
    }
    
    /* Universal High-Contrast HUD */
    .hud-card {
        background-color: var(--hud-bg) !important;
        border: 2px solid var(--card-border) !important;
        border-radius: 16px !important;
        padding: 18px 24px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45) !important;
    }
    .hud-title {
        font-size: 1.45rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin: 0 !important;
    }
    .hud-label {
        font-size: 0.75rem !important;
        color: #94a3b8 !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em !important;
    }
    .hud-value {
        font-size: 1.15rem !important;
        font-weight: 800 !important;
    }
    
    /* Universal Notebook Card */
    .notebook-card {
        background-color: #1a1608 !important;
        border: 2px dashed var(--gold-bright) !important;
        border-left: 6px solid var(--gold-bright) !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        margin-bottom: 18px !important;
    }
    .notebook-title {
        color: var(--gold-bright) !important;
        font-size: 0.85rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        margin-bottom: 6px !important;
    }
    .notebook-rule {
        color: #ffffff !important;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        line-height: 1.4 !important;
    }
    .notebook-rule strong, .notebook-rule b {
        color: #fde047 !important;
        font-weight: 800 !important;
    }

    /* Universal Stimulus Context Box */
    .stimulus-box {
        background-color: #0d1527 !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        margin: 14px 0px !important;
        font-size: 1.05rem !important;
        color: #f1f5f9 !important;
        line-height: 1.5 !important;
    }
    .stimulus-box strong {
        color: #38bdf8 !important;
        font-weight: 800 !important;
    }

    /* Universal Plain-English Box */
    .plain-tag {
        background-color: var(--blue-bg) !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        border-left: 4px solid var(--blue-bright) !important;
        color: #f0f9ff !important;
        padding: 10px 16px !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        margin-bottom: 16px !important;
        line-height: 1.45 !important;
    }
    .plain-tag strong {
        color: var(--blue-bright) !important;
    }

    /* Enforce High Contrast on Question Headers */
    .question-header {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        line-height: 1.4 !important;
        margin: 12px 0 16px 0 !important;
    }
    .question-header strong {
        color: #facc15 !important;
        font-weight: 800 !important;
    }

    /* Interactive Buttons */
    div.stButton > button:first-child {
        border-radius: 10px !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.15s ease-in-out !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# API CLIENT INITIALIZATION
# ---------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("🔑 Critical: GEMINI_API_KEY is missing in Streamlit Secrets.")
    st.stop()


@st.cache_resource
def get_ai_client(key: str):
    return genai.Client(api_key=key)


client = get_ai_client(api_key)


# Clean markdown asterisks into HTML strong tags for reliable rendering
def format_bold_html(text: str) -> str:
    if not text:
        return ""
    # Convert **bold** to <strong>bold</strong>
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", str(text))
    # Replace any accidental programming symbols with school arithmetic symbols
    text = text.replace(" * ", " × ").replace(" / ", " ÷ ")
    return text


# ---------------------------------------------------------
# DETERMINISTIC PROCEDURAL ENGINE (Offline Zero-Latency Core)
# ---------------------------------------------------------
def generate_procedural_speed():
    speed = random.choice([12, 15, 18, 24, 30, 36, 45, 60])
    expected = (speed * 1000) // 60
    return {
        "topic": "Speed, Distance & Time",
        "requires_working": False,
        "clean_target": str(expected),
        "stimulus": (
            "A commuter travels on an e-scooter at a constant speed of"
            f" <strong>{speed} km/h</strong> along a cycleway."
        ),
        "question": (
            "How many <strong>metres</strong> does the rider cover in"
            " <strong>one single minute</strong>?"
        ),
        "plain_english": (
            "Multiply kilometres by 1,000 to get metres, then divide by 60"
            " minutes to find 1 minute."
        ),
        "notebook_rule": (
            "<strong>Metres per min = (Speed in km/h × 1,000) ÷ 60</strong>"
        ),
        "expected_answer": f"{expected} metres",
        "hint_1": (
            "Step 1: Convert to metres per hour: <strong>"
            f"{speed} × 1,000 = {speed * 1000} m</strong>."
        ),
        "hint_2": (
            "Step 2: Divide by 60 minutes: <strong>"
            f"{speed * 1000} ÷ 60</strong>."
        ),
        "solution": (
            f"Convert to metres: <strong>{speed} × 1,000 = {speed * 1000}"
            " m/h</strong>.<br>Divide for 1 minute: <strong>"
            f"{speed * 1000} ÷ 60 = {expected} metres</strong>."
        ),
    }


def generate_procedural_mass():
    unit_price = round(random.uniform(7.50, 14.50), 2)
    grams = random.choice([450, 650, 760, 850, 920, 1250])
    total_cost = round((grams / 1000) * unit_price, 2)
    return {
        "topic": "Mass Conversions & Rates",
        "requires_working": False,
        "clean_target": f"{total_cost:.2f}",
        "stimulus": (
            "Diced chicken is priced at <strong>"
            f"${unit_price:.2f} per kilogram</strong>. A package weighs"
            f" <strong>{grams} grams</strong>."
        ),
        "question": (
            "Calculate the total cost of this package in dollars and cents."
        ),
        "plain_english": (
            "Convert grams to kilograms (divide by 1,000), then multiply by the"
            " price per kg."
        ),
        "notebook_rule": (
            "<strong>Total Cost = (Grams ÷ 1,000) × Price per kg</strong>"
        ),
        "expected_answer": f"${total_cost:.2f}",
        "hint_1": (
            "Step 1: Turn grams into kg: <strong>"
            f"{grams} ÷ 1,000 = {grams / 1000} kg</strong>."
        ),
        "hint_2": (
            "Step 2: Multiply by rate: <strong>"
            f"{grams / 1000} × ${unit_price:.2f}</strong>."
        ),
        "solution": (
            f"Convert grams to kg: <strong>{grams} ÷ 1,000 = {grams / 1000}"
            " kg</strong>.<br>Calculate price: <strong>"
            f"{grams / 1000} × ${unit_price:.2f} = ${total_cost:.2f}</strong>."
        ),
    }


def generate_procedural_capacity():
    drinkers = random.choice([16, 20, 24, 28, 32])
    serving_ml = random.choice([250, 300, 350, 500])
    total_ml = drinkers * serving_ml
    total_litres = total_ml / 1000
    return {
        "topic": "Capacity & Volume Planning",
        "requires_working": False,
        "clean_target": f"{total_litres:g}",
        "stimulus": (
            f"A school camp serves drinks to <strong>{drinkers}"
            f" students</strong>. Each student gets <strong>{serving_ml}"
            " mL</strong> of water."
        ),
        "question": (
            "How many <strong>Litres</strong> of water are needed in total?"
        ),
        "plain_english": (
            "Multiply students by mL, then divide by 1,000 to convert to"
            " Litres."
        ),
        "notebook_rule": (
            "<strong>Total Litres = (Students × mL per serving) ÷"
            " 1,000</strong>"
        ),
        "expected_answer": f"{total_litres:g} L",
        "hint_1": (
            "Step 1: Total volume in mL: <strong>"
            f"{drinkers} × {serving_ml} = {total_ml} mL</strong>."
        ),
        "hint_2": (
            "Step 2: Convert to Litres: <strong>"
            f"{total_ml} ÷ 1,000</strong>."
        ),
        "solution": (
            f"Total mL: <strong>{drinkers} × {serving_ml} = {total_ml}"
            " mL</strong>.<br>Convert to Litres: <strong>"
            f"{total_ml} ÷ 1,000 = {total_litres:g} Litres</strong>."
        ),
    }


def generate_procedural_claim():
    normal_price = random.choice([80, 100, 120, 150])
    two_pairs_regular = normal_price * 2
    deal_total = normal_price + (normal_price // 2)
    savings = two_pairs_regular - deal_total
    pct_save = int((savings / two_pairs_regular) * 100)
    return {
        "topic": "Outcome 3 Claims (Agree / Disagree)",
        "requires_working": True,
        "clean_target": "disagree",
        "stimulus": (
            "A shoe store deal: <strong>'Buy one pair for"
            f" ${normal_price}</strong>, get the second identical pair for"
            " <strong>half price</strong>.'"
        ),
        "question": (
            "A customer claims: 'Because the second pair is 50% off, I am"
            " saving 50% on my total order.' Do you agree or disagree? Explain"
            " using numbers."
        ),
        "plain_english": (
            "Work out the normal cost for 2 pairs vs what you pay, and find the"
            " actual percentage saved."
        ),
        "notebook_rule": (
            "<strong>Saving % = (Total Dollars Saved ÷ Total Original Price) ×"
            " 100</strong>"
        ),
        "expected_answer": (
            f"Disagree: Actual saving is {pct_save}%, not 50%."
        ),
        "hint_1": (
            "Step 1: Normal cost: <strong>"
            f"${normal_price} × 2 = ${two_pairs_regular}</strong>."
        ),
        "hint_2": (
            "Step 2: Deal price: <strong>"
            f"${normal_price} + ${normal_price // 2} = ${deal_total}</strong>."
            f" Saving = <strong>${savings}</strong>."
        ),
        "solution": (
            "<strong>I Disagree.</strong><br>Regular price: <strong>"
            f"${normal_price} × 2 = ${two_pairs_regular}</strong>.<br>Deal"
            f" price: <strong>${normal_price} + ${normal_price // 2} ="
            f" ${deal_total}</strong>.<br>Dollars saved: <strong>"
            f"${savings}</strong>.<br>Actual discount: <strong>"
            f"(${savings} ÷ ${two_pairs_regular}) × 100 = {pct_save}%</strong>,"
            " NOT 50%."
        ),
    }


PROCEDURAL_GENERATORS = [
    generate_procedural_speed,
    generate_procedural_mass,
    generate_procedural_capacity,
    generate_procedural_claim,
]

# ----------------- SESSION STATE HYDRATION -----------------
DEFAULTS = {
    "xp": 0,
    "streak": 0,
    "solved": 0,
    "session_start": time.time(),
    "scenario": None,
    "feedback": None,
    "hint_level": 0,
    "struggling_topics": [],
    "chat_log": [
        {
            "role": "assistant",
            "content": (
                "Kia ora! I am your 24/7 CAA AI Coach. Ask me how to convert"
                " units, solve speed equations, or write Agree/Disagree claims!"
            ),
        }
    ],
}

for key, default_val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default_val


def dispatch_next_challenge():
    # If the student struggled, prompt Gemini for remediation; otherwise use zero-latency procedural core
    if st.session_state.struggling_topics and random.random() < 0.5:
        target_concept = st.session_state.struggling_topics[-1]
        prompt = f"""
        Generate one authentic NCEA Numeracy CAA (Unit Standard 32406) question targeting: {target_concept}.
        MANDATORY RULES:
        1. All formulas and equations must use standard symbols: '×' and '÷'. Never use '*' or '/'.
        2. Set 'clean_target' to the exact numeric answer string.
        3. Output valid raw JSON only with NO markdown fences:
        {{
          "topic": "{target_concept}",
          "requires_working": false,
          "clean_target": "250",
          "stimulus": "Data context or scenario",
          "question": "Clear problem statement",
          "plain_english": "1-sentence plain summary",
          "notebook_rule": "Metres per min = (Speed in km/h × 1,000) ÷ 60",
          "expected_answer": "Final string",
          "hint_1": "Step 1 text",
          "hint_2": "Step 2 text",
          "solution": "Full worked solution using × and ÷"
        }}
        """
        try:
            res = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )
            raw = res.text.strip()
            if raw.startswith("```"):
                raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw).strip()
            st.session_state.scenario = json.loads(raw)
            st.session_state.hint_level = 0
            st.session_state.feedback = None
            return
        except Exception:
            pass

    # Instant Local Procedural Engine
    engine_func = random.choice(PROCEDURAL_GENERATORS)
    st.session_state.scenario = engine_func()
    st.session_state.hint_level = 0
    st.session_state.feedback = None


if st.session_state.scenario is None:
    dispatch_next_challenge()

# ----------------- NOTEBOOK FLASHCARDS -----------------
STUDY_NOTEBOOK = {
    "Speed, Distance & Time": """
    ### 📓 CORE NOTEBOOK DIRECTIVES:
    * **Speed Formula:** **Speed = Distance ÷ Time**
    * **Distance Formula:** **Distance = Speed × Time**
    * **Time Formula:** **Time = Distance ÷ Speed**
    * **Speed Conversion:** **Metres per min = (Speed in km/h × 1,000) ÷ 60**
    * **The Base-60 Watchout:** Time is **base-60**, NOT base-100!
      * **2.5 hours = 2 hours and 30 minutes = 150 minutes** (NEVER 2 hours 50 mins!)
      * **1.25 hours = 1 hour and 15 minutes = 75 minutes**
    """,
    "Mass & Capacity (kg, g, L, mL)": """
    ### 📓 CORE NOTEBOOK DIRECTIVES:
    * **Mass Relationship:** **1 kg = 1,000 g**
      * **Kilograms to Grams:** Multiply by 1,000 (**kg × 1,000 = g**)
      * **Grams to Kilograms:** Divide by 1,000 (**g ÷ 1,000 = kg**)
    * **Supermarket Pricing:** **Cost = (Mass in Grams ÷ 1,000) × Price per kg**
    * **Capacity Relationship:** **1 Litre = 1,000 mL**
      * **Total Litres Needed = (Attendees × mL per serving) ÷ 1,000**
    """,
    "Percentages & Outcome 3 Claims": """
    ### 📓 CORE NOTEBOOK DIRECTIVES:
    * **Percentage Discount:** **Discount % = (Dollars Saved ÷ Original Price) × 100**
    * **The 'Buy 1 Get 2nd Half Price' Trap:** Saves **25% on the entire order, NOT 50%!**
    * **Outcome 3 Assessment Standards:**
      1. Always declare position: **"I agree"** or **"I disagree"**.
      2. Quote at least **two numerical values or percentages** as evidence.
      3. State the comparative logic clearly (e.g. **"59 out of 100 is 59%, which exceeds 50%"**).
    """,
}

# ----------------- PROGRESSION HUD -----------------
elapsed_seconds = time.time() - st.session_state.session_start
mins_remaining = max(0, 30 - int(elapsed_seconds / 60))

rank_title = (
    "👑 CAA Grandmaster"
    if st.session_state.xp >= 350
    else (
        "🥇 Elite Scholar"
        if st.session_state.xp >= 200
        else (
            "🥈 Senior Apprentice"
            if st.session_state.xp >= 80
            else "🥉 Junior Candidate"
        )
    )
)

st.markdown(
    f"""
<div class="hud-card">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
        <div>
            <div class="hud-label" style="color: #38bdf8 !important;">NCEA UNIT STANDARD 32406</div>
            <div class="hud-title">CAA High-Velocity Arena</div>
        </div>
        <div style="display: flex; gap: 24px; align-items: center;">
            <div style="text-align: right;">
                <div class="hud-label">CURRENT RANK</div>
                <div class="hud-value" style="color: #facc15 !important;">{rank_title}</div>
            </div>
            <div style="background: #334155; width: 2px; height: 32px;"></div>
            <div style="text-align: right;">
                <div class="hud-label">STREAK</div>
                <div class="hud-value" style="color: #fb923c !important;">🔥 {st.session_state.streak}x</div>
            </div>
            <div style="background: #334155; width: 2px; height: 32px;"></div>
            <div style="text-align: right;">
                <div class="hud-label">RUN TIME</div>
                <div class="hud-value" style="color: #38bdf8 !important;">⏳ {mins_remaining}m left</div>
            </div>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

if st.session_state.struggling_topics:
    st.info(
        f"🎯 **AI Adaptation Radar Active:** Re-enforcing priority standards: **{', '.join(set(st.session_state.struggling_topics))}**"
    )

with st.expander("📖 Interactive CAA Reference Notebook (Formulas & Traps)"):
    tab1, tab2, tab3 = st.tabs(list(STUDY_NOTEBOOK.keys()))
    for tab, (key, doc) in zip([tab1, tab2, tab3], STUDY_NOTEBOOK.items()):
        with tab:
            st.markdown(doc)

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# ----------------- MAIN ARENA -----------------
col_arena, col_coach = st.columns([1.35, 1], gap="large")

with col_arena:
    q_col1, q_col2 = st.columns([3, 1])
    with q_col1:
        st.markdown(
            "<div style='font-size: 0.9rem; font-weight: 800; color: #94a3b8;"
            " text-transform: uppercase; letter-spacing: 0.05em;'>Standard"
            f" Strand: {st.session_state.scenario.get('topic')}</div>",
            unsafe_allow_html=True,
        )
    with q_col2:
        if st.button("🔄 Next Question", use_container_width=True):
            dispatch_next_challenge()
            st.rerun()

    current_q = st.session_state.scenario

    # Actionable Notebook Banner (Guaranteed Bold via HTML)
    if current_q.get("notebook_rule"):
        formatted_rule = format_bold_html(current_q.get("notebook_rule"))
        st.markdown(
            f"""
        <div class="notebook-card">
            <div class="notebook-title">📓 Write This In Your Notebook</div>
            <div class="notebook-rule">{formatted_rule}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Data Context Stimulus
    if current_q.get("stimulus"):
        formatted_stimulus = format_bold_html(current_q.get("stimulus"))
        st.markdown(
            f"""
        <div class="stimulus-box">
            <strong style="color: #38bdf8; display: block; margin-bottom: 4px;">📊 Context / Scenario Data:</strong>
            {formatted_stimulus}
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Problem Statement
    formatted_question = format_bold_html(current_q.get("question"))
    st.markdown(
        f"<div class='question-header'>{formatted_question}</div>",
        unsafe_allow_html=True,
    )

    # Plain English Breakdown
    formatted_plain = format_bold_html(current_q.get("plain_english"))
    st.markdown(
        f"""
    <div class="plain-tag">
        <strong>💡 Plain English Guide:</strong> {formatted_plain}
    </div>
    """,
        unsafe_allow_html=True,
    )

    needs_working = current_q.get("requires_working", False)

    # Form Wrapper for Instant Mobile Keyboard Submissions
    with st.form(key="solution_form"):
        if needs_working:
            st.markdown(
                "<strong style='color: #ffffff; font-size: 0.95rem;'>✍️ Write"
                " your equations or explain your Agree/Disagree stance with"
                " numbers:</strong>",
                unsafe_allow_html=True,
            )
            user_response = st.text_area(
                "Student Submission",
                key="input_working",
                label_visibility="collapsed",
                placeholder=(
                    "Type your equations or state your Agree/Disagree stance"
                    " with numbers..."
                ),
                height=95,
            )
        else:
            st.markdown(
                "<strong style='color: #ffffff; font-size: 0.95rem;'>⚡ Instant"
                " Answer Entry:</strong>",
                unsafe_allow_html=True,
            )
            user_response = st.text_input(
                "Student Submission",
                key="input_direct",
                label_visibility="collapsed",
                placeholder="Enter value (e.g. 250, $6.80, or 45)...",
            )

        submit_btn = st.form_submit_button(
            "🚀 Verify Answer", type="primary", use_container_width=True
        )

    if submit_btn:
        if not user_response.strip():
            st.warning("Please enter an answer before verifying.")
        else:
            clean_target = (
                str(current_q.get("clean_target", "")).strip().lower()
            )
            clean_input = re.sub(r"[^\w.]", "", user_response.lower())

            # Local High-Speed Evaluation (0.00s latency)
            is_valid = False
            if not needs_working:
                clean_target_num = re.sub(r"[^\w.]", "", clean_target)
                if clean_target_num and (
                    clean_target_num in clean_input
                    or clean_input in clean_target_num
                ):
                    is_valid = True
            else:
                if "disagree" in clean_target and "disagree" in clean_input:
                    is_valid = True

            if is_valid:
                st.session_state.streak += 1
                earned_xp = 30 + (st.session_state.streak * 5)
                st.session_state.xp += earned_xp
                st.session_state.solved += 1

                t = current_q.get("topic")
                if t in st.session_state.struggling_topics:
                    st.session_state.struggling_topics.remove(t)

                st.session_state.feedback = {
                    "status": "correct",
                    "title": f"Exceptional Work! (+{earned_xp} XP)",
                    "body": format_bold_html(current_q.get("solution")),
                }
                if st.session_state.streak % 3 == 0:
                    st.balloons()
            else:
                st.session_state.streak = 0
                topic_tag = current_q.get("topic")
                if (
                    topic_tag
                    and topic_tag not in st.session_state.struggling_topics
                ):
                    st.session_state.struggling_topics.append(topic_tag)

                st.session_state.feedback = {
                    "status": "incorrect",
                    "title": "Review Required",
                    "body": format_bold_html(current_q.get("solution")),
                }

    if st.session_state.feedback:
        fb = st.session_state.feedback
        if fb["status"] == "correct":
            st.success(f"**{fb['title']}**\n\n{fb['body']}")
        else:
            st.error(
                f"**{fb['title']}**\n\n**Correct Working &"
                f" Equations:**\n\n{fb['body']}"
            )

    with st.expander("💡 Scaffolded Step-by-Step Hints"):
        if st.session_state.hint_level >= 1:
            st.info(f"**Step 1:** {format_bold_html(current_q.get('hint_1'))}")
        if st.session_state.hint_level >= 2:
            st.info(f"**Step 2:** {format_bold_html(current_q.get('hint_2'))}")
        if st.session_state.hint_level >= 3:
            st.success(
                f"**Full Solution:** {format_bold_html(current_q.get('solution'))}"
            )

        if st.session_state.hint_level < 3:
            if st.button("Unlock Next Step"):
                st.session_state.hint_level += 1
                st.rerun()

# ----------------- AI TUTOR COPILOT (HIGH-VISIBILITY) -----------------
with col_coach:
    st.markdown("### 🤖 24/7 AI Numeracy Tutor")
    st.caption("Ask questions about any conversion, equation, or formula.")

    chat_container = st.container(height=420)
    for chat_item in st.session_state.chat_log:
        with chat_container.chat_message(chat_item["role"]):
            st.markdown(chat_item["content"])

    user_query = st.chat_input("Ask: e.g. How do I convert 100mL to L?")
    if user_query:
        q_low = user_query.lower()
        st.session_state.chat_log.append(
            {"role": "user", "content": user_query}
        )
        with chat_container.chat_message("user"):
            st.markdown(user_query)

        # Local High-Speed Conversions (Instant response, no API quota consumed)
        local_reply = None

        if "ml to l" in q_low or "millilitre" in q_low or "100ml" in q_low:
            local_reply = """
            **Converting mL to Litres:**
            * **Rule:** Divide the number of millilitres by **1,000**.
            * **Equation:** **mL ÷ 1,000 = Litres**
            * **Example:** **100 mL ÷ 1,000 = 0.1 Litres**
            * 📓 **Notebook Rule:** **1,000 mL = 1 Litre**
            """
        elif "l to ml" in q_low or "litre to" in q_low:
            local_reply = """
            **Converting Litres to mL:**
            * **Rule:** Multiply the number of litres by **1,000**.
            * **Equation:** **Litres × 1,000 = mL**
            * **Example:** **2.5 L × 1,000 = 2,500 mL**
            * 📓 **Notebook Rule:** **1 Litre = 1,000 mL**
            """
        elif (
            "km/h to m/min" in q_low
            or "km to m" in q_low
            or "speed" in q_low
            or "metres per min" in q_low
        ):
            local_reply = """
            **Converting km/h to Metres per Minute:**
            * **Step 1:** Multiply km/h by 1,000 to get metres in one hour (**km/h × 1,000**).
            * **Step 2:** Divide by 60 to find distance in one minute (**÷ 60**).
            * **Example:** **36 km/h × 1,000 = 36,000 m/h**; then **36,000 ÷ 60 = 600 m/min**.
            * 📓 **Notebook Rule:** **Metres per min = (Speed in km/h × 1,000) ÷ 60**
            """
        elif "kg to g" in q_low or "kilo" in q_low:
            local_reply = """
            **Converting Kilograms to Grams:**
            * **Rule:** Multiply kilograms by **1,000**.
            * **Equation:** **kg × 1,000 = grams**
            * **Example:** **1.2 kg × 1,000 = 1,200 g**
            * 📓 **Notebook Rule:** **1 kg = 1,000 g**
            """
        elif "g to kg" in q_low:
            local_reply = """
            **Converting Grams to Kilograms:**
            * **Rule:** Divide grams by **1,000**.
            * **Equation:** **grams ÷ 1,000 = kg**
            * **Example:** **760 g ÷ 1,000 = 0.76 kg**
            * 📓 **Notebook Rule:** **Grams ÷ 1,000 = kg**
            """
        elif "percent" in q_low or "discount" in q_low or "gst" in q_low:
            local_reply = """
            **Percentage & Discount Rules:**
            * **Percentage Discount:** **Discount % = (Dollars Saved ÷ Original Price) × 100**
            * **15% GST Rule:** **Total with GST = Price × 1.15**
            * 📓 **The Trap:** Buy 1 get 2nd half-price saves **25% on the total purchase, NOT 50%!**
            """
        elif (
            "2.5" in q_low
            or "decimal time" in q_low
            or "hours to min" in q_low
            or "time" in q_low
        ):
            local_reply = """
            **The Base-60 Time Rule:**
            * Time is **base-60**, NOT base-100!
            * **2.5 hours = 2 hours and 30 minutes = 150 minutes** (never 2 hours 50 mins!)
            * **1.25 hours = 1 hour and 15 minutes = 75 minutes**
            * 📓 **Notebook Rule:** Multiply decimal parts by 60 (**0.5 × 60 = 30 minutes**).
            """

        if local_reply:
            reply = local_reply.strip()
        else:
            context = f"Question: {current_q.get('question')} | Stimulus: {current_q.get('stimulus')}"
            full_prompt = f"""
            You are a helpful NCEA CAA Numeracy tutor (Unit Standard 32406).
            Context: {context}
            Student query: {user_query}
            
            RULES:
            - Format ALL formulas, arithmetic steps, and equations in **BOLD**.
            - Always use standard school symbols: '×' and '÷'. Never use '*' or '/'.
            - Keep answers short (under 3 bullets) and give the exact rule to write in their notebook.
            """
            try:
                bot_res = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=full_prompt,
                )
                reply = (
                    bot_res.text
                    if bot_res.text
                    else "Check your **Interactive Reference Notebook** above for this rule!"
                )
            except Exception as err:
                reply = (
                    "**Tutor Note:** Check the **Interactive Reference"
                    " Notebook** tab above for the formula! (Status Note:"
                    f" {err})"
                )

        st.session_state.chat_log.append(
            {"role": "assistant", "content": reply}
        )
        with chat_container.chat_message("assistant"):
            st.markdown(reply)
