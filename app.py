import html
import json
import os
import random
import re
import time
import streamlit as st

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
        --hud-bg: #0f172a !important;
        --card-border: #334155 !important;
        --gold-bright: #fbbf24 !important;
        --gold-bg: rgba(251, 191, 36, 0.14) !important;
        --blue-bright: #38bdf8 !important;
        --blue-bg: rgba(56, 189, 248, 0.1) !important;
    }

    * { font-family: 'Plus Jakarta Sans', -apple-system, sans-serif; }
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1100px; }
    
    /* Universal HUD Card */
    .hud-card {
        background-color: var(--hud-bg) !important;
        border: 2px solid var(--card-border) !important;
        border-radius: 16px !important;
        padding: 16px 22px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45) !important;
    }
    .hud-title {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin: 0 !important;
    }
    .hud-label {
        font-size: 0.72rem !important;
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
        padding: 14px 18px !important;
        margin-bottom: 16px !important;
    }
    .notebook-title {
        color: var(--gold-bright) !important;
        font-size: 0.85rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
    }
    .notebook-rule {
        color: #ffffff !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        line-height: 1.4 !important;
    }
    .notebook-rule strong, .notebook-rule b {
        color: #fde047 !important;
        font-weight: 800 !important;
    }

    /* Scenario / Story Box */
    .story-box {
        background-color: #0d1527 !important;
        border: 1px solid var(--card-border) !important;
        border-left: 5px solid #38bdf8 !important;
        border-radius: 12px !important;
        padding: 18px 22px !important;
        margin: 14px 0px !important;
        font-size: 1.05rem !important;
        color: #f1f5f9 !important;
        line-height: 1.55 !important;
    }
    .story-box strong { color: #38bdf8 !important; font-weight: 800 !important; }

    /* Plain English Summary Tag */
    .plain-tag {
        background-color: var(--blue-bg) !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
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
        margin: 14px 0 16px 0 !important;
    }
    .question-header strong { color: #facc15 !important; font-weight: 800 !important; }

    /* Level Badges */
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

    /* Primary Action Buttons */
    div.stButton > button {
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
# OPTIONAL BACKGROUND AI CLIENT (LOADS SAFELY WITHOUT HANGING)
# ---------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY")
client = None
if api_key:
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
    except Exception:
        client = None

def format_bold_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", str(text))
    return text.replace(" * ", " × ").replace(" / ", " ÷ ")

# ---------------------------------------------------------
# PROCEDURAL LEVEL 1: FOUNDATION CAA (1-Step)
# ---------------------------------------------------------
def gen_lvl1_mass():
    kg = random.choice([1.2, 1.5, 2.4, 3.5, 4.2])
    expected = int(kg * 1000)
    return {
        "level": 1,
        "topic": "Mass: Kilograms to Grams",
        "requires_working": False,
        "clean_target": str(expected),
        "story": f"Liam is packing a tramping pack for an overnight trip in Arthur's Pass. His portable camp stove and cookware weigh exactly <strong>{kg} kilograms</strong> in total.",
        "question": f"What is the total weight of Liam's cooking gear in <strong>grams</strong>?",
        "plain_english": "Multiply the kilograms by 1,000 to convert to grams.",
        "notebook_rule": "<strong>Grams = Kilograms × 1,000</strong>",
        "expected_answer": f"{expected} g",
        "hint_1": "Step 1: Remember that 1 kg = 1,000 grams.",
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
        "story": f"During rugby practice, the team manager fills a heavy-duty insulated water container with <strong>{ml} millilitres</strong> of cold water for the bench players.",
        "question": f"How many <strong>Litres</strong> of water are in the container?",
        "plain_english": "Divide the millilitres by 1,000 to find the answer in Litres.",
        "notebook_rule": "<strong>Litres = Millilitres ÷ 1,000</strong>",
        "expected_answer": f"{expected:g} L",
        "hint_1": "Step 1: Remember that 1,000 mL = 1 Litre.",
        "hint_2": f"Step 2: Calculate <strong>{ml} ÷ 1,000</strong>.",
        "solution": f"Calculation: <strong>{ml} ÷ 1,000 = {expected:g} Litres</strong>.",
    }

# ---------------------------------------------------------
# PROCEDURAL LEVEL 2: APPLIED MULTI-STEP (Stories & Budgets)
# ---------------------------------------------------------
def gen_lvl2_supermarket_story():
    sausages_kg = random.choice([3, 4, 5])
    chicken_kg = random.choice([2, 2.5, 3.5])
    s_cost = sausages_kg * 11
    c_cost = chicken_kg * 9
    total_spent = s_cost + c_cost
    expected = int(100 - total_spent)
    
    events = [
        "organising a community barbecue for their local touch rugby club",
        "shopping at the local supermarket for a Sunday family gathering",
        "preparing a sausage sizzle fundraiser outside the hardware store"
    ]
    selected_event = random.choice(events)

    return {
        "level": 2,
        "topic": "Rates & Supermarket Budgeting",
        "requires_working": False,
        "clean_target": str(expected),
        "story": f"Aroha is {selected_event}. Her committee gave her a single <strong>$100 note</strong> to buy meat. At the butchery, pre-packed sausages cost <strong>$11 per kg</strong> (she grabs <strong>{sausages_kg} kg</strong>) and chicken drumsticks cost <strong>$9 per kg</strong> (she grabs <strong>{chicken_kg} kg</strong>).",
        "question": "About how many dollars in change does Aroha have left over from her $100 note after paying?",
        "plain_english": "Work out the cost of sausages, add the cost of chicken, and subtract that total from $100.",
        "notebook_rule": "<strong>Change = Budget - [(kg₁ × $/kg₁) + (kg₂ × $/kg₂)]</strong>",
        "expected_answer": f"${expected}",
        "hint_1": f"Step 1: Sausages = <strong>{sausages_kg} × $11 = ${s_cost}</strong>. Chicken = <strong>{chicken_kg} × $9 = ${c_cost}</strong>.",
        "hint_2": f"Step 2: Total cost = <strong>${s_cost} + ${c_cost} = ${total_spent}</strong>.",
        "solution": f"Sausages: <strong>{sausages_kg} × $11 = ${s_cost}</strong>.<br>Chicken: <strong>{chicken_kg} × $9 = ${c_cost}</strong>.<br>Total spent: <strong>${total_spent}</strong>.<br>Change from $100: <strong>$100 - ${total_spent} = ${expected}</strong>.",
    }

def gen_lvl2_speed_story():
    speed = random.choice([15, 18, 24, 30, 36, 45, 60])
    expected = (speed * 1000) // 60
    return {
        "level": 2,
        "topic": "Speed & Unit Rates (km/h to m/min)",
        "requires_working": False,
        "clean_target": str(expected),
        "story": f"Tane commutes to his polytechnic course every morning on an electric scooter. His dashboard speedometer shows he is maintaining a steady speed of <strong>{speed} km/h</strong> along the city cycle path.",
        "question": f"At this steady speed, how many <strong>metres</strong> does Tane travel forward in <strong>one single minute</strong>?",
        "plain_english": "Multiply by 1,000 to convert to metres per hour, then divide by 60 minutes for 1 minute.",
        "notebook_rule": "<strong>Metres per min = (Speed in km/h × 1,000) ÷ 60</strong>",
        "expected_answer": f"{expected} metres",
        "hint_1": f"Step 1: Metres in 1 hour: <strong>{speed} × 1,000 = {speed * 1000} m</strong>.",
        "hint_2": f"Step 2: Divide by 60: <strong>{speed * 1000} ÷ 60</strong>.",
        "solution": f"Distance in 1 hour: <strong>{speed} × 1,000 = {speed * 1000} m</strong>.<br>Distance in 1 minute: <strong>{speed * 1000} ÷ 60 = {expected} metres</strong>.",
    }

# ---------------------------------------------------------
# PROCEDURAL LEVEL 3: EXAM BOSS (Outcome 3 Claims)
# ---------------------------------------------------------
def gen_lvl3_claim_discount_story():
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
        "story": f"A sports shoe retailer launches a back-to-school sale: <em>'Buy one pair of basketball boots for <strong>${normal_price}</strong>, get a second identical pair for <strong>half price</strong>.'</em>",
        "question": "A student customer tells his friends: 'Because the second pair is 50% off, we are saving 50% on our whole purchase.' Do you agree or disagree? Justify your decision using exact numbers.",
        "plain_english": "Calculate what two pairs normally cost, what you actually pay with the deal, and find the real percentage saved.",
        "notebook_rule": "<strong>Actual Saving % = (Total Dollars Saved ÷ Total Original Price) × 100</strong>",
        "expected_answer": f"Disagree: Actual saving is {pct_save}%, not 50%.",
        "hint_1": f"Step 1: Normal cost of 2 pairs: <strong>${normal_price} × 2 = ${two_pairs_regular}</strong>.",
        "hint_2": f"Step 2: You pay <strong>${normal_price} + ${normal_price // 2} = ${deal_total}</strong>. Saved = <strong>${savings}</strong>.",
        "solution": f"<strong>I Disagree.</strong><br>Regular price: <strong>${normal_price} × 2 = ${two_pairs_regular}</strong>.<br>Deal price: <strong>${normal_price} + ${normal_price // 2} = ${deal_total}</strong>.<br>Total saved: <strong>${savings}</strong>.<br>Actual saving: <strong>(${savings} ÷ ${two_pairs_regular}) × 100 = {pct_save}%</strong>, which is NOT 50%.",
    }

def gen_lvl3_data_frequency_story():
    return {
        "level": 3,
        "topic": "Outcome 3: Frequency Distribution Claim",
        "requires_working": True,
        "clean_target": "agree",
        "story": "A cycle safety organisation tested the durability of 100 bike helmets during impact trials: <strong>41 helmets</strong> suffered damage before 18 months of simulated use; <strong>59 helmets</strong> showed zero cracks and lasted 18 months or longer.",
        "question": "The safety inspector claims: 'More than half of the tested helmets lasted 18 months or longer.' Do you agree or disagree? Explain using numbers.",
        "plain_english": "Check whether 59 out of 100 helmets is strictly greater than half (50%).",
        "notebook_rule": "<strong>Comparison Rule: Always state your position and cite exact numerical evidence.</strong>",
        "expected_answer": "Agree: 59 out of 100 is 59%, which is greater than half (50).",
        "hint_1": "Step 1: Half of 100 helmets is exactly <strong>50 helmets (50%)</strong>.",
        "hint_2": "Step 2: Compare 59 helmets to 50 helmets.",
        "solution": "<strong>I Agree.</strong> Half of the sample of 100 helmets is <strong>50 helmets (50%)</strong>.<br>The trial data shows <strong>59 helmets</strong> lasted 18 months or more, and <strong>59 is greater than 50</strong>.",
    }

LEVEL_1_POOL = [gen_lvl1_mass, gen_lvl1_capacity]
LEVEL_2_POOL = [gen_lvl2_supermarket_story, gen_lvl2_speed_story]
LEVEL_3_POOL = [gen_lvl3_claim_discount_story, gen_lvl3_data_frequency_story]

# ---------------------------------------------------------
# SESSION STATE HYDRATION
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
    "q_counter": 1,  # Used to uniquely clear the input field on new questions
}

for key, default_val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default_val

def dispatch_next_challenge():
    st.session_state.q_counter += 1
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

# ---------------------------------------------------------
# UI: TOP PROGRESSION HUD
# ---------------------------------------------------------
elapsed_seconds = time.time() - st.session_state.session_start
mins_remaining = max(0, 30 - int(elapsed_seconds / 60))

lvl_name = (
    "Level 1: Foundation" if st.session_state.current_level == 1
    else "Level 2: Applied CAA" if st.session_state.current_level == 2
    else "Level 3: Exam Boss"
)
next_tier_progress = f"{st.session_state.consecutive_at_level} / 2 to Rank Up"

st.markdown(f"""
<div class="hud-card">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
        <div>
            <div class="hud-label" style="color: #38bdf8 !important;">NCEA NUMERACY UNIT STANDARD 32406</div>
            <div class="hud-title">CAA High-Velocity Arena</div>
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
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HIGH-PRIORITY NOTEBOOK REFERENCE TABLE (Always Visible)
# ---------------------------------------------------------
st.markdown("""
<div style="background-color: #0f172a; border: 2px solid #334155; border-radius: 12px; padding: 16px; margin-bottom: 20px;">
    <div style="font-size: 0.9rem; font-weight: 800; color: #fbbf24; text-transform: uppercase; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
        📓 Master Notebook Reference (Formulas & Traps)
    </div>
    <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 0.95rem; color: #e2e8f0; text-align: left;">
            <thead>
                <tr style="border-bottom: 2px solid #334155; color: #38bdf8;">
                    <th style="padding: 8px 12px;">Topic Strand</th>
                    <th style="padding: 8px 12px;">Core Formula to Write Down</th>
                    <th style="padding: 8px 12px;">Key CAA Exam Trap</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #1e293b;">
                    <td style="padding: 8px 12px; font-weight: 700;">Speed & Time</td>
                    <td style="padding: 8px 12px;"><strong>Metres per min = (Speed in km/h × 1,000) ÷ 60</strong></td>
                    <td style="padding: 8px 12px; color: #f87171;">Time is base-60! 2.5 hrs = 2h 30m (150 mins), NEVER 2h 50m.</td>
                </tr>
                <tr style="border-bottom: 1px solid #1e293b;">
                    <td style="padding: 8px 12px; font-weight: 700;">Mass (kg & g)</td>
                    <td style="padding: 8px 12px;"><strong>kg × 1,000 = grams</strong> | <strong>grams ÷ 1,000 = kg</strong></td>
                    <td style="padding: 8px 12px; color: #f87171;">Turn grams to kg BEFORE multiplying by $/kg price!</td>
                </tr>
                <tr style="border-bottom: 1px solid #1e293b;">
                    <td style="padding: 8px 12px; font-weight: 700;">Capacity (L & mL)</td>
                    <td style="padding: 8px 12px;"><strong>1 Litre = 1,000 mL</strong> (Total L = People × mL ÷ 1,000)</td>
                    <td style="padding: 8px 12px; color: #f87171;">Do not add Litres and mL directly without converting first.</td>
                </tr>
                <tr>
                    <td style="padding: 8px 12px; font-weight: 700;">Outcome 3 Claims</td>
                    <td style="padding: 8px 12px;"><strong>Discount % = (Dollars Saved ÷ Original Cost) × 100</strong></td>
                    <td style="padding: 8px 12px; color: #f87171;">"Buy 1 get 2nd half-price" saves 25% on total, NOT 50%!</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MAIN WORKSPACE: ACTIVE QUESTION STAGE
# ---------------------------------------------------------
current_q = st.session_state.scenario
badge_class = f"badge-lvl-{current_q.get('level', 1)}"

st.markdown(f"<span class='level-badge {badge_class}'>Level {current_q.get('level')} • {current_q.get('topic')}</span>", unsafe_allow_html=True)

# Copy to Notebook Directive
if current_q.get("notebook_rule"):
    formatted_rule = format_bold_html(current_q.get("notebook_rule"))
    st.markdown(f"""
    <div class="notebook-card">
        <div class="notebook-title">📓 Write This Formula In Your Notebook</div>
        <div class="notebook-rule">{formatted_rule}</div>
    </div>
    """, unsafe_allow_html=True)

# Story Scenario Box
if current_q.get("story"):
    formatted_story = format_bold_html(current_q.get("story"))
    st.markdown(f"""
    <div class="story-box">
        <strong style="color: #38bdf8; display: block; margin-bottom: 6px;">📖 Context & Story:</strong>
        {formatted_story}
    </div>
    """, unsafe_allow_html=True)

# Problem Question Header
formatted_question = format_bold_html(current_q.get("question"))
st.markdown(f"<div class='question-header'>{formatted_question}</div>", unsafe_allow_html=True)

# Plain English Helper
formatted_plain = format_bold_html(current_q.get("plain_english"))
st.markdown(f"""
<div class="plain-tag">
    <strong>💡 Plain English Guide:</strong> {formatted_plain}
</div>
""", unsafe_allow_html=True)

needs_working = current_q.get("requires_working", False)

# Form wraps the input and actions; dynamic key clears answer automatically on question change
input_key = f"ans_{st.session_state.q_counter}"

with st.form(key="caa_form"):
    if needs_working:
        st.markdown("<strong style='color: #ffffff; font-size: 0.95rem;'>✍️ State your Agree/Disagree verdict and justify with numbers:</strong>", unsafe_allow_html=True)
        user_response = st.text_area(
            "Student Submission",
            key=input_key,
            label_visibility="collapsed",
            placeholder="e.g. I disagree because normal price is $200 and you save $50, which is 25%...",
            height=95
        )
    else:
        st.markdown("<strong style='color: #ffffff; font-size: 0.95rem;'>⚡ Instant Answer Entry:</strong>", unsafe_allow_html=True)
        user_response = st.text_input(
            "Student Submission",
            key=input_key,
            label_visibility="collapsed",
            placeholder="Enter value (e.g. 250, $25, 1200)..."
        )

    # Action Buttons: Verify Answer and Next Question Side-by-Side
    btn_col1, btn_col2 = st.columns([1.5, 1])
    with btn_col1:
        submit_btn = st.form_submit_button("🚀 Verify Answer", type="primary", use_container_width=True)
    with btn_col2:
        skip_btn = st.form_submit_button("🔄 Next Question ❯", use_container_width=True)

# Handle Next Question button within form
if skip_btn:
    dispatch_next_challenge()
    st.rerun()

# Handle Answer Verification (Zero AI Token Overhead, Instant 0.00s grading)
if submit_btn:
    if not user_response.strip():
        st.warning("Please enter your answer before verifying.")
    else:
        clean_target = str(current_q.get("clean_target", "")).strip().lower()
        clean_input = re.sub(r"[^\w.]", "", user_response.lower())

        is_valid = False
        if not needs_working:
            clean_target_num = re.sub(r"[^\w.]", "", clean_target)
            if clean_target_num and (clean_target_num in clean_input or clean_input in clean_target_num):
                is_valid = True
        else:
            if clean_target in clean_input:
                is_valid = True

        if is_valid:
            st.session_state.streak += 1
            st.session_state.solved += 1
            st.session_state.consecutive_at_level += 1
            earned_xp = (30 * st.session_state.current_level) + (st.session_state.streak * 5)
            st.session_state.xp += earned_xp

            leveled_up = False
            if st.session_state.consecutive_at_level >= 2 and st.session_state.current_level < 3:
                st.session_state.current_level += 1
                st.session_state.consecutive_at_level = 0
                leveled_up = True
                st.balloons()

            st.session_state.feedback = {
                "status": "correct",
                "title": f"🎉 LEVEL UP! Promoted to Level {st.session_state.current_level}!" if leveled_up else f"Exceptional Work! (+{earned_xp} XP)",
                "body": format_bold_html(current_q.get("solution"))
            }
        else:
            st.session_state.streak = 0
            st.session_state.consecutive_at_level = 0
            if st.session_state.current_level > 1:
                st.session_state.current_level -= 1

            st.session_state.feedback = {
                "status": "incorrect",
                "title": "Review Required (Reinforcing Concept)",
                "body": format_bold_html(current_q.get("solution"))
            }

# Render Feedback Banner
if st.session_state.feedback:
    fb = st.session_state.feedback
    if fb["status"] == "correct":
        st.success(f"**{fb['title']}**\n\n{fb['body']}")
    else:
        st.error(f"**{fb['title']}**\n\n**Correct Working & Equations:**\n\n{fb['body']}")

# Scaffolded Step-by-Step Hints Accordion
with st.expander("💡 Need Step-by-Step Help?"):
    if st.session_state.hint_level >= 1:
        st.info(f"**Step 1:** {format_bold_html(current_q.get('hint_1'))}")
    if st.session_state.hint_level >= 2:
        st.info(f"**Step 2:** {format_bold_html(current_q.get('hint_2'))}")
    if st.session_state.hint_level >= 3:
        st.success(f"**Full Solution:** {format_bold_html(current_q.get('solution'))}")
        
    if st.session_state.hint_level < 3:
        if st.button("Unlock Next Step"):
            st.session_state.hint_level += 1
            st.rerun()
