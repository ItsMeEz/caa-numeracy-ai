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
    page_title="Apex Numeracy | NCEA CAA Mastery Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    :root {
        --text-headline: #ffffff !important;
        --text-sub: #cbd5e1 !important;
        --hud-bg: #0f172a !important;
        --card-border: #334155 !important;
        --gold-bright: #fbbf24 !important;
        --gold-bg: rgba(251, 191, 36, 0.16) !important;
        --blue-bright: #38bdf8 !important;
        --blue-bg: rgba(56, 189, 248, 0.12) !important;
        --purple-bright: #c084fc !important;
    }

    * { font-family: 'Plus Jakarta Sans', -apple-system, sans-serif; }
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1250px; }
    
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
    
    /* Notebook Directive Card */
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

    /* Stimulus Context Box */
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
    .stimulus-box strong { color: #38bdf8 !important; font-weight: 800 !important; }

    /* Plain English Callout */
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
    .plain-tag strong { color: var(--blue-bright) !important; }

    /* Question Header */
    .question-header {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        line-height: 1.4 !important;
        margin: 12px 0 16px 0 !important;
    }
    .question-header strong { color: #facc15 !important; font-weight: 800 !important; }

    /* Level Indicator Badge */
    .level-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .badge-lvl-1 { background: rgba(34, 197, 94, 0.2); border: 1px solid #22c55e; color: #4ade80; }
    .badge-lvl-2 { background: rgba(56, 189, 248, 0.2); border: 1px solid #38bdf8; color: #7dd3fc; }
    .badge-lvl-3 { background: rgba(192, 132, 252, 0.2); border: 1px solid #c084fc; color: #e9d5ff; }

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


def format_bold_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", str(text))
    return text.replace(" * ", " × ").replace(" / ", " ÷ ")


# ---------------------------------------------------------
# PROCEDURAL LEVEL 1: FOUNDATION CAA (Single-Step)
# ---------------------------------------------------------
def gen_lvl1_mass():
    kg = random.choice([1.2, 1.5, 2.4, 3.5, 4.2])
    expected = int(kg * 1000)
    return {
        "level": 1,
        "topic": "Mass: Kilograms to Grams",
        "requires_working": False,
        "clean_target": str(expected),
        "stimulus": f"A bag of apples weighs <strong>{kg} kilograms</strong>.",
        "question": f"What is the weight of the apples in <strong>grams</strong>?",
        "plain_english": "Multiply kilograms by 1,000 to convert to grams.",
        "notebook_rule": "<strong>Grams = Kilograms × 1,000</strong>",
        "expected_answer": f"{expected} g",
        "hint_1": f"Step 1: Remember that 1 kg = 1,000 grams.",
        "hint_2": f"Step 2: Calculate <strong>{kg} × 1,000</strong>.",
        "solution": f"Calculation: <strong>{kg} × 1,000 = {expected} grams</strong>.",
    }


def gen_lvl1_capacity():
    ml = random.choice([2500, 3200, 4500, 1800, 5500])
    expected = ml / 1000
    return {
        "level": 1,
        "topic": "Capacity: mL to Litres",
        "requires_working": False,
        "clean_target": f"{expected:g}",
        "stimulus": f"A water cooler contains <strong>{ml} millilitres</strong> of cold water.",
        "question": f"How many <strong>Litres</strong> of water are in the cooler?",
        "plain_english": "Divide millilitres by 1,000 to convert into Litres.",
        "notebook_rule": "<strong>Litres = Millilitres ÷ 1,000</strong>",
        "expected_answer": f"{expected:g} L",
        "hint_1": f"Step 1: Remember that 1,000 mL = 1 Litre.",
        "hint_2": f"Step 2: Calculate <strong>{ml} ÷ 1,000</strong>.",
        "solution": f"Calculation: <strong>{ml} ÷ 1,000 = {expected:g} Litres</strong>.",
    }


# ---------------------------------------------------------
# PROCEDURAL LEVEL 2: APPLIED MULTI-STEP (2 Correct Unlocked)
# ---------------------------------------------------------
def gen_lvl2_speed():
    speed = random.choice([15, 18, 24, 30, 36, 45, 60])
    expected = (speed * 1000) // 60
    return {
        "level": 2,
        "topic": "Speed & Unit Rates (km/h to m/min)",
        "requires_working": False,
        "clean_target": str(expected),
        "stimulus": f"An electric scooter travels at an average speed of <strong>{speed} km/h</strong>.",
        "question": f"How many <strong>metres</strong> does the scooter travel in <strong>one single minute</strong>?",
        "plain_english": "Change kilometres to metres (times 1,000), then divide by 60 minutes for 1 minute.",
        "notebook_rule": "<strong>Metres per min = (Speed in km/h × 1,000) ÷ 60</strong>",
        "expected_answer": f"{expected} metres",
        "hint_1": f"Step 1: Metres per hour: <strong>{speed} × 1,000 = {speed * 1000} m</strong>.",
        "hint_2": f"Step 2: Divide for 1 minute: <strong>{speed * 1000} ÷ 60</strong>.",
        "solution": f"Convert to metres: <strong>{speed} × 1,000 = {speed * 1000} m/h</strong>.<br>For 1 minute: <strong>{speed * 1000} ÷ 60 = {expected} metres</strong>.",
    }


def gen_lvl2_supermarket():
    sausages_kg = random.choice([3, 4, 5])
    chicken_kg = random.choice([2, 2.5, 3.5])
    s_cost = sausages_kg * 11
    c_cost = chicken_kg * 9
    total_cost = s_cost + c_cost
    expected = int(100 - total_cost)
    return {
        "level": 2,
        "topic": "Rates & Supermarket Budgeting",
        "requires_working": False,
        "clean_target": str(expected),
        "stimulus": f"You have $100. Sausages cost $11/kg (you buy <strong>{sausages_kg} kg</strong>). Chicken costs $9/kg (you buy <strong>{chicken_kg} kg</strong>).",
        "question": "About how many dollars do you have left over from your $100 note?",
        "plain_english": "Calculate the sausage cost, add the chicken cost, and subtract the total from $100.",
        "notebook_rule": "<strong>Change = Budget - [(kg₁ × $/kg₁) + (kg₂ × $/kg₂)]</strong>",
        "expected_answer": f"${expected}",
        "hint_1": f"Step 1: Sausages = <strong>{sausages_kg} × $11 = ${s_cost}</strong>. Chicken = <strong>{chicken_kg} × $9 = ${c_cost}</strong>.",
        "hint_2": f"Step 2: Total spent = <strong>${s_cost} + ${c_cost} = ${total_cost}</strong>.",
        "solution": f"Sausages: <strong>{sausages_kg} × $11 = ${s_cost}</strong>. Chicken: <strong>{chicken_kg} × $9 = ${c_cost}</strong>.<br>Total spent: <strong>${total_cost}</strong>. Change from $100: <strong>$100 - ${total_cost} = ${expected}</strong>.",
    }


# ----------------- PROCEDURAL LEVEL 3: EXAM BOSS (4 Correct Unlocked) -----------------
def gen_lvl3_claim_discount():
    normal_price = random.choice([80, 100, 120, 150])
    two_pairs_regular = normal_price * 2
    deal_total = normal_price + (normal_price // 2)
    savings = two_pairs_regular - deal_total
    pct_save = int((savings / two_pairs_regular) * 100)
    return {
        "level": 3,
        "topic": "Outcome 3 Claims (Agree / Disagree)",
        "requires_working": True,
        "clean_target": "disagree",
        "stimulus": f"A footwear store advertises: 'Buy one pair of sneakers for <strong>${normal_price}</strong>, get the second pair for <strong>half price</strong>.'",
        "question": "A buyer claims: 'Because the second pair is 50% off, I save 50% on my total order.' Do you agree or disagree? Explain using exact numbers.",
        "plain_english": "Calculate total normal cost vs promotional cost, and find the real percentage saved.",
        "notebook_rule": "<strong>Actual Saving % = (Total Dollars Saved ÷ Total Original Cost) × 100</strong>",
        "expected_answer": f"Disagree: Actual saving is {pct_save}%, not 50%.",
        "hint_1": f"Step 1: Normal price for 2 pairs: <strong>${normal_price} × 2 = ${two_pairs_regular}</strong>.",
        "hint_2": f"Step 2: Deal price: <strong>${normal_price} + ${normal_price // 2} = ${deal_total}</strong>. Saved = <strong>${savings}</strong>.",
        "solution": f"<strong>I Disagree.</strong><br>Regular price: <strong>${normal_price} × 2 = ${two_pairs_regular}</strong>.<br>Deal price: <strong>${normal_price} + ${normal_price // 2} = ${deal_total}</strong>.<br>Total saved: <strong>${savings}</strong>.<br>Actual saving: <strong>(${savings} ÷ ${two_pairs_regular}) × 100 = {pct_save}%</strong>, which is NOT 50%.",
    }


def gen_lvl3_data_frequency():
    return {
        "level": 3,
        "topic": "Outcome 3: Frequency Distribution Claim",
        "requires_working": True,
        "clean_target": "agree",
        "stimulus": "A quality test recorded the lifespans of 100 skateboard wheels: <strong>41 wheels</strong> wore out in under 9 months; <strong>59 wheels</strong> lasted 9 months or longer.",
        "question": "The manufacturer claims: 'More than half of our tested wheels lasted 9 months or longer.' Do you agree or disagree? Explain using numbers.",
        "plain_english": "Check whether 59 out of 100 is strictly greater than half (50%).",
        "notebook_rule": "<strong>Comparison Rule: Always state position and cite exact numerical frequencies.</strong>",
        "expected_answer": "Agree: 59 out of 100 is 59%, which is greater than half (50).",
        "hint_1": "Step 1: Identify that 'half' of 100 wheels is exactly <strong>50 wheels</strong>.",
        "hint_2": "Step 2: Compare 59 to 50.",
        "solution": "<strong>I Agree.</strong> Half of the sample of 100 wheels is <strong>50 wheels (50%)</strong>.<br>The data shows <strong>59 wheels</strong> lasted 9 months or more, and <strong>59 is greater than 50</strong>.",
    }


LEVEL_1_POOL = [gen_lvl1_mass, gen_lvl1_capacity]
LEVEL_2_POOL = [gen_lvl2_speed, gen_lvl2_supermarket]
LEVEL_3_POOL = [gen_lvl3_claim_discount, gen_lvl3_data_frequency]

# ---------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------
DEFAULTS = {
    "xp": 0,
    "streak": 0,
    "solved": 0,
    "current_level": 1,
    "consecutive_at_level": 0,
    "session_start": time.time(),
    "scenario": None,
    "feedback": None,
    "hint_level": 0,
    "struggling_topics": [],
    "chat_log": [
        {
            "role": "assistant",
            "content": "Kia ora! I am your 24/7 CAA AI Coach. Get 2 consecutive correct answers to advance to harder CAA exam questions!",
        }
    ],
}

for key, default_val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default_val


def dispatch_next_challenge():
    lvl = st.session_state.current_level
    if lvl == 1:
        engine = random.choice(LEVEL_1_POOL)
    elif lvl == 2:
        engine = random.choice(LEVEL_2_POOL)
    else:
        engine = random.choice(LEVEL_3_POOL)

    st.session_state.scenario = engine()
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
    * **Unit Conversion (km/h to m/min):** **Metres per min = (Speed in km/h × 1,000) ÷ 60**
    * **The Base-60 Watchout:** Time is **base-60**, not base-100!
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

lvl_name = (
    "Level 1: Foundation"
    if st.session_state.current_level == 1
    else (
        "Level 2: Applied CAA"
        if st.session_state.current_level == 2
        else "Level 3: Exam Boss"
    )
)
next_tier_progress = f"{st.session_state.consecutive_at_level} / 2 to Rank Up"

st.markdown(
    f"""
<div class="hud-card">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
        <div>
            <div class="hud-label" style="color: #38bdf8 !important;">NCEA NUMERACY UNIT STANDARD 32406</div>
            <div class="hud-title">CAA Mastery Arena</div>
        </div>
        <div style="display: flex; gap: 20px; align-items: center;">
            <div style="text-align: right;">
                <div class="hud-label">CURRENT DIFFICULTY</div>
                <div class="hud-value" style="color: #facc15 !important;">{lvl_name}</div>
            </div>
            <div style="background: #334155; width: 2px; height: 32px;"></div>
            <div style="text-align: right;">
                <div class="hud-label">TIER PROGRESSION</div>
                <div class="hud-value" style="color: #4ade80 !important;">{next_tier_progress}</div>
            </div>
            <div style="background: #334155; width: 2px; height: 32px;"></div>
            <div style="text-align: right;">
                <div class="hud-label">STREAK</div>
                <div class="hud-value" style="color: #fb923c !important;">🔥 {st.session_state.streak}x</div>
            </div>
            <div style="background: #334155; width: 2px; height: 32px;"></div>
            <div style="text-align: right;">
                <div class="hud-label">TIME LEFT</div>
                <div class="hud-value" style="color: #38bdf8 !important;">⏳ {mins_remaining}m</div>
            </div>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
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
    current_q = st.session_state.scenario
    badge_class = f"badge-lvl-{current_q.get('level', 1)}"

    q_col1, q_col2 = st.columns([3, 1])
    with q_col1:
        st.markdown(
            f"<span class='level-badge {badge_class}'>Level"
            f" {current_q.get('level')} • {current_q.get('topic')}</span>",
            unsafe_allow_html=True,
        )
    with q_col2:
        if st.button("🔄 Next Question", use_container_width=True):
            dispatch_next_challenge()
            st.rerun()

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

    formatted_question = format_bold_html(current_q.get("question"))
    st.markdown(
        f"<div class='question-header'>{formatted_question}</div>",
        unsafe_allow_html=True,
    )

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

    with st.form(key="solution_form"):
        if needs_working:
            st.markdown(
                "<strong style='color: #ffffff; font-size: 0.95rem;'>✍️ State"
                " your Agree/Disagree verdict and explain using"
                " numbers:</strong>",
                unsafe_allow_html=True,
            )
            user_response = st.text_area(
                "Student Submission",
                key="input_working",
                label_visibility="collapsed",
                placeholder=(
                    "e.g. I disagree because normal price is $200 and you save"
                    " $50 which is 25%..."
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
                placeholder="Enter value (e.g. 250, $25, 1200)...",
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

            is_valid = False
            if not needs_working:
                clean_target_num = re.sub(r"[^\w.]", "", clean_target)
                if clean_target_num and (
                    clean_target_num in clean_input
                    or clean_input in clean_target_num
                ):
                    is_valid = True
            else:
                if clean_target in clean_input:
                    is_valid = True

            if is_valid:
                st.session_state.streak += 1
                st.session_state.solved += 1
                st.session_state.consecutive_at_level += 1
                earned_xp = (
                    30 * st.session_state.current_level
                    + (st.session_state.streak * 5)
                )
                st.session_state.xp += earned_xp

                # Level Up Condition: 2 consecutive correct answers at current tier
                leveled_up = False
                if (
                    st.session_state.consecutive_at_level >= 2
                    and st.session_state.current_level < 3
                ):
                    st.session_state.current_level += 1
                    st.session_state.consecutive_at_level = 0
                    leveled_up = True
                    st.balloons()

                st.session_state.feedback = {
                    "status": "correct",
                    "title": (
                        f"🎉 LEVEL UP! Promoted to Level"
                        f" {st.session_state.current_level}!"
                        if leveled_up
                        else f"Exceptional Work! (+{earned_xp} XP)"
                    ),
                    "body": format_bold_html(current_q.get("solution")),
                }
            else:
                st.session_state.streak = 0
                st.session_state.consecutive_at_level = 0
                # If they struggle at Level 3, drop back to Level 2 for remediation
                if st.session_state.current_level > 1:
                    st.session_state.current_level -= 1

                st.session_state.feedback = {
                    "status": "incorrect",
                    "title": "Review Required (Returning to Reinforce Concept)",
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

# ----------------- AI TUTOR COPILOT -----------------
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

        local_reply = None

        if "ml to l" in q_low or "millilitre" in q_low or "100ml" in q_low:
            local_reply = """
            **Converting mL to Litres:**
            * **Rule:** Divide millilitres by **1,000**.
            * **Equation:** **mL ÷ 1,000 = Litres**
            * **Example:** **100 mL ÷ 1,000 = 0.1 Litres**
            * 📓 **Notebook Rule:** **1,000 mL = 1 Litre**
            """
        elif "l to ml" in q_low or "litre to" in q_low:
            local_reply = """
            **Converting Litres to mL:**
            * **Rule:** Multiply litres by **1,000**.
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
        elif "percent" in q_low or "discount" in q_low:
            local_reply = """
            **Percentage & Discount Rules:**
            * **Percentage Discount:** **Discount % = (Dollars Saved ÷ Original Price) × 100**
            * 📓 **The Trap:** Buy 1 get 2nd half-price saves **25% on the total purchase, NOT 50%!**
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
