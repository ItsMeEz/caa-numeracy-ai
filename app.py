import html
import json
import os
import random
import re
import time
import streamlit as st
from google import genai
from google.genai import types

# ---------------------------------------------------------
# PLATFORM CONFIGURATION & DESIGN SYSTEM
# ---------------------------------------------------------
st.set_page_config(
    page_title="Apex Numeracy | NCEA CAA Core Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom Design System (Clean Glassmorphism & High-Contrast Scaffolding)
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }

    /* Core Canvas Clean-up */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1250px;
    }
    
    /* Sleek HUD Header */
    .hud-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.85));
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 18px 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.36);
    }
    
    /* Notebook Directive Banner */
    .notebook-card {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.12), rgba(217, 119, 6, 0.05));
        border-left: 5px solid #f59e0b;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 18px;
    }
    .notebook-title {
        color: #fbbf24;
        font-size: 0.8rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .notebook-rule {
        color: #ffffff;
        font-size: 1.15rem;
        font-weight: 700;
    }

    /* Stimulus / Data Presentation Box */
    .stimulus-box {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 14px 18px;
        margin: 14px 0px;
        font-size: 0.95rem;
        color: #cbd5e1;
    }

    /* Sub-text clarification badge */
    .plain-tag {
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #7dd3fc;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 0.88rem;
        margin-bottom: 16px;
    }

    /* Primary Interactive Buttons */
    div.stButton > button:first-child {
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.95rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 14px rgba(0,0,0,0.3);
    }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# BACKEND API & CLIENT INITIALIZATION
# ---------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("🔑 Critical: GEMINI_API_KEY is missing in Streamlit Secrets.")
    st.stop()

@st.cache_resource
def get_ai_client(key: str):
    return genai.Client(api_key=key)

client = get_ai_client(api_key)

# ---------------------------------------------------------
# DETERMINISTIC PROCEDURAL ENGINE (Zero-Latency Core)
# ---------------------------------------------------------
# Dynamic algorithm engines producing infinite valid CAA items without API stalls
def generate_procedural_speed():
    speed = random.choice([12, 15, 18, 24, 30, 36, 45, 60])
    expected = (speed * 1000) // 60
    return {
        "topic": "Speed, Distance & Time",
        "requires_working": False,
        "clean_target": str(expected),
        "stimulus": f"A commuter rides an electric scooter along an urban cycleway at an average speed of **{speed} km/h**.",
        "question": f"How many **metres** does the rider travel in **one single minute**?",
        "plain_english": "Change kilometres to metres (times 1,000), then divide by 60 minutes to find the distance for 1 minute.",
        "notebook_rule": "**Metres per min = (Speed in km/h × 1,000) ÷ 60**",
        "expected_answer": f"{expected} metres",
        "hint_1": f"Step 1: Calculate metres in 1 hour: **{speed} × 1,000 = {speed * 1000} m**.",
        "hint_2": f"Step 2: Divide that total by 60 minutes: **{speed * 1000} ÷ 60**.",
        "solution": f"Convert to metres: **{speed} × 1,000 = {speed * 1000} m/h**. Per minute: **{speed * 1000} ÷ 60 = {expected} metres**.",
    }

def generate_procedural_mass():
    unit_price = round(random.uniform(7.50, 14.50), 2)
    grams = random.choice([450, 650, 760, 850, 920, 1250])
    total_cost = round((grams / 1000) * unit_price, 2)
    return {
        "topic": "Mass Conversions & Supermarket Rates",
        "requires_working": False,
        "clean_target": f"{total_cost:.2f}",
        "stimulus": f"Premium beef mince is priced at **${unit_price:.2f} per kilogram**. A shopper selects a package marked **{grams} grams**.",
        "question": f"Calculate the exact total cost of this package in dollars and cents.",
        "plain_english": "Convert the grams to kilograms (divide by 1,000), then multiply by the price per kg.",
        "notebook_rule": "**Total Cost = (Grams ÷ 1,000) × Price per kg**",
        "expected_answer": f"${total_cost:.2f}",
        "hint_1": f"Step 1: Turn grams into kilograms: **{grams} ÷ 1,000 = {grams / 1000} kg**.",
        "hint_2": f"Step 2: Multiply by unit price: **{grams / 1000} × ${unit_price:.2f}**.",
        "solution": f"Convert mass: **{grams} ÷ 1,000 = {grams / 1000} kg**. Calculate price: **{grams / 1000} × {unit_price:.2f} = ${total_cost:.2f}**.",
    }

def generate_procedural_capacity():
    drinkers = random.choice([16, 20, 24, 28, 32])
    serving_ml = random.choice([250, 300, 350, 500])
    total_ml = drinkers * serving_ml
    total_litres = total_ml / 1000
    return {
        "topic": "Capacity & Event Planning",
        "requires_working": False,
        "clean_target": f"{total_litres:g}",
        "stimulus": f"A school sports council is catering an event for **{drinkers} athletes**. Each athlete is allocated **{serving_ml} mL** of electrolyte water.",
        "question": f"How many **Litres** of electrolyte water must the council mix in total?",
        "plain_english": "Find the total millilitres needed (people times mL), then divide by 1,000 to convert to Litres.",
        "notebook_rule": "**Total Litres = (Number of People × mL per person) ÷ 1,000**",
        "expected_answer": f"{total_litres:g} L",
        "hint_1": f"Step 1: Calculate total mL: **{drinkers} × {serving_ml} = {total_ml} mL**.",
        "hint_2": f"Step 2: Convert mL to Litres: **{total_ml} ÷ 1,000**.",
        "solution": f"Total volume: **{drinkers} × {serving_ml} = {total_ml} mL**. Convert to litres: **{total_ml} ÷ 1,000 = {total_litres:g} Litres**.",
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
        "stimulus": f"A footwear store advertises: 'Buy one pair of sneakers for **${normal_price}**, get the second identical pair for **half price**.'",
        "question": "A customer claims: 'Because the second pair is 50% off, I am saving 50% on my total order.' Do you agree or disagree? Justify your decision with clear numbers.",
        "plain_english": "Calculate the full price for two pairs, compare it to what you actually pay, and work out the real percentage saved.",
        "notebook_rule": "**Actual Discount % = (Total Dollars Saved ÷ Total Original Price) × 100**",
        "expected_answer": f"Disagree: The actual saving is {pct_save}%, not 50%.",
        "hint_1": f"Step 1: Full cost of 2 pairs: **${normal_price} + ${normal_price} = ${two_pairs_regular}**.",
        "hint_2": f"Step 2: Deal price: **${normal_price} + ${normal_price // 2} = ${deal_total}**. Dollars saved = **${savings}**.",
        "solution": f"**I Disagree.** Regular cost: **${normal_price} × 2 = ${two_pairs_regular}**. Promotional cost: **${normal_price} + ${normal_price // 2} = ${deal_total}**. Total savings: **${savings}**. Actual saving percentage: **(${savings} ÷ ${two_pairs_regular}) × 100 = {pct_save}%**, NOT 50%.",
    }

PROCEDURAL_GENERATORS = [
    generate_procedural_speed,
    generate_procedural_mass,
    generate_procedural_capacity,
    generate_procedural_claim,
]

# ---------------------------------------------------------
# SESSION STATE HYDRATION
# ---------------------------------------------------------
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
        {"role": "assistant", "content": "Kia ora! I am your 24/7 CAA AI Coach. Need help setting up an equation or finding a step? Ask me below!"}
    ]
}

for key, default_val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default_val

# ---------------------------------------------------------
# QUESTION DISPATCH CONTROLLER
# ---------------------------------------------------------
def dispatch_next_challenge():
    # If the user has a recurring mistake, query Gemini with a strict timeout; otherwise fire instant procedural engine
    if st.session_state.struggling_topics and random.random() < 0.65:
        target_concept = st.session_state.struggling_topics[-1]
        system_instruction = """
        You are an elite NCEA Numeracy examiner for New Zealand Standard 32406.
        Generate a rigorous question targeting the student's weak concept.
        
        CRITICAL RULES:
        1. All formulas, equations, and mathematical steps MUST BE IN BOLD with standard school symbols: '×' and '÷'. Never use '*' or '/'.
        2. Set 'clean_target' to the pure numeric answer string (e.g. '250', '6.80').
        3. Output MUST be valid raw JSON only.
        
        Schema:
        {
          "topic": "Topic Name",
          "requires_working": false,
          "clean_target": "string",
          "stimulus": "Data context or scenario",
          "question": "Clear problem statement",
          "plain_english": "1-sentence summary",
          "notebook_rule": "**Bold equation to remember**",
          "expected_answer": "Final string",
          "hint_1": "Step 1 with bold equations",
          "hint_2": "Step 2 with bold equations",
          "solution": "Full worked solution with bold equations using × and ÷"
        }
        """
        try:
            res = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=f"Generate an authentic remediation CAA question targeting: {target_concept}.",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                ),
            )
            st.session_state.scenario = json.loads(res.text)
            st.session_state.hint_level = 0
            st.session_state.feedback = None
            return
        except Exception:
            pass  # Fail gracefully to procedural core below
            
    # Procedural Core Execution (Immediate, Zero API overhead)
    engine_func = random.choice(PROCEDURAL_GENERATORS)
    st.session_state.scenario = engine_func()
    st.session_state.hint_level = 0
    st.session_state.feedback = None

if st.session_state.scenario is None:
    dispatch_next_challenge()

# ---------------------------------------------------------
# INTERACTIVE STUDY NOTEBOOK SPECIFICATIONS
# ---------------------------------------------------------
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
    """
}

# ---------------------------------------------------------
# UI: TOP-TIER HUD & PROGRESSION BAR
# ---------------------------------------------------------
elapsed_seconds = time.time() - st.session_state.session_start
mins_remaining = max(0, 30 - int(elapsed_seconds / 60))

# Level Bracket Architecture
rank_title = (
    "👑 CAA Grandmaster" if st.session_state.xp >= 350
    else "🥇 Elite Scholar" if st.session_state.xp >= 200
    else "🥈 Senior Apprentice" if st.session_state.xp >= 80
    else "🥉 Junior Candidate"
)

st.markdown(f"""
<div class="hud-card">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div>
            <div style="font-size: 0.78rem; font-weight: 800; color: #38bdf8; letter-spacing: 0.08em; text-transform: uppercase;">NCEA Unit Standard 32406</div>
            <div style="font-size: 1.4rem; font-weight: 800; color: #ffffff;">CAA High-Velocity Arena</div>
        </div>
        <div style="display: flex; gap: 20px; align-items: center;">
            <div style="text-align: right;">
                <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">ACTIVE RANK</div>
                <div style="font-size: 1.05rem; font-weight: 800; color: #facc15;">{rank_title}</div>
            </div>
            <div style="background: rgba(255,255,255,0.08); width: 1px; height: 32px;"></div>
            <div style="text-align: right;">
                <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">STREAK</div>
                <div style="font-size: 1.05rem; font-weight: 800; color: #fb923c;">🔥 {st.session_state.streak}x</div>
            </div>
            <div style="background: rgba(255,255,255,0.08); width: 1px; height: 32px;"></div>
            <div style="text-align: right;">
                <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">RUN TIME</div>
                <div style="font-size: 1.05rem; font-weight: 800; color: #38bdf8;">⏳ {mins_remaining}m left</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Adaptive Remediation Alert
if st.session_state.struggling_topics:
    st.info(f"🎯 **AI Adaptation Radar Active:** Re-enforcing priority standards: **{', '.join(set(st.session_state.struggling_topics))}**")

# Interactive Lesson Notebook Expanders
with st.expander("📖 Interactive CAA Reference Notebook (Formulas & Traps)"):
    tab1, tab2, tab3 = st.tabs(list(STUDY_NOTEBOOK.keys()))
    for tab, (key, doc) in zip([tab1, tab2, tab3], STUDY_NOTEBOOK.items()):
        with tab:
            st.markdown(doc)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# MAIN WORKSPACE: ARENA STAGE (COL 1) & AI COACH (COL 2)
# ---------------------------------------------------------
col_arena, col_coach = st.columns([1.35, 1], gap="large")

with col_arena:
    q_col1, q_col2 = st.columns([3, 1])
    with q_col1:
        st.markdown(f"<div style='font-size: 0.85rem; font-weight: 700; color: #94a3b8; text-transform: uppercase;'>Standard Strand: {st.session_state.scenario.get('topic')}</div>", unsafe_allow_html=True)
    with q_col2:
        if st.button("🔄 Next Question", use_container_width=True):
            dispatch_next_challenge()
            st.rerun()

    current_q = st.session_state.scenario

    # Actionable Notebook Banner
    if current_q.get("notebook_rule"):
        safe_rule = html.escape(str(current_q.get("notebook_rule"))).replace("&lt;strong&gt;", "<strong>").replace("&lt;/strong&gt;", "</strong>")
        st.markdown(f"""
        <div class="notebook-card">
            <div class="notebook-title">📓 Write This In Your Notebook</div>
            <div class="notebook-rule">{current_q.get('notebook_rule')}</div>
        </div>
        """, unsafe_allow_html=True)

    # Data Context Stimulus
    if current_q.get("stimulus"):
        st.markdown(f"<div class='stimulus-box'>📊 <strong>Context / Scenario Data:</strong><br>{current_q.get('stimulus')}</div>", unsafe_allow_html=True)

    # Problem Statement
    st.markdown(f"### {current_q.get('question')}")
    st.markdown(f"<div class='plain-tag'>💡 <strong>Plain English Guide:</strong> {current_q.get('plain_english')}</div>", unsafe_allow_html=True)

    # Adaptive Input Routing
    needs_working = current_q.get("requires_working", False)
    if needs_working:
        st.markdown("✍️ **Show Your Equations or Explain Your Verdict with Numbers:**")
        user_response = st.text_area(
            "Student Submission",
            key="input_working",
            label_visibility="collapsed",
            placeholder="Type your equations or state your Agree/Disagree stance with numbers...",
            height=100
        )
    else:
        st.markdown("⚡ **Instant Answer Entry:**")
        user_response = st.text_input(
            "Student Submission",
            key="input_direct",
            label_visibility="collapsed",
            placeholder="Enter value (e.g. 250, $6.80, or 45)..."
        )

    # Evaluation Controller
    if st.button("🚀 Verify Answer", type="primary", use_container_width=True):
        if not user_response.strip():
            st.warning("Please provide an answer before submitting.")
        else:
            clean_target = str(current_q.get("clean_target", "")).strip().lower()
            clean_input = re.sub(r"[^\w.]", "", user_response.lower())
            
            # Local Ultra-Fast Evaluation Path
            is_valid = False
            if not needs_working:
                clean_target_num = re.sub(r"[^\w.]", "", clean_target)
                if clean_target_num and (clean_target_num in clean_input or clean_input in clean_target_num):
                    is_valid = True
            else:
                if "disagree" in clean_target and "disagree" in clean_input:
                    is_valid = True

            if is_valid:
                st.session_state.streak += 1
                earned_xp = 30 + (st.session_state.streak * 5)
                st.session_state.xp += earned_xp
                st.session_state.solved += 1
                
                # Resolve topic from struggling radar if mastered
                t = current_q.get("topic")
                if t in st.session_state.struggling_topics:
                    st.session_state.struggling_topics.remove(t)
                    
                st.session_state.feedback = {
                    "status": "correct",
                    "title": f"Exceptional Work! (+{earned_xp} XP)",
                    "body": current_q.get("solution")
                }
                if st.session_state.streak % 3 == 0:
                    st.balloons()
            else:
                st.session_state.streak = 0
                topic_tag = current_q.get("topic")
                if topic_tag and topic_tag not in st.session_state.struggling_topics:
                    st.session_state.struggling_topics.append(topic_tag)
                    
                st.session_state.feedback = {
                    "status": "incorrect",
                    "title": "Review Required",
                    "body": current_q.get("solution")
                }

    # Render Feedback Box
    if st.session_state.feedback:
        fb = st.session_state.feedback
        if fb["status"] == "correct":
            st.success(f"**{fb['title']}**\n\n{fb['body']}")
        else:
            st.error(f"**{fb['title']}**\n\n**Correct Working & Equations:**\n\n{fb['body']}")

    # Progressive Scaffolded Hints
    with st.expander("💡 Scaffolded Step-by-Step Hints"):
        if st.session_state.hint_level >= 1:
            st.info(f"**Step 1:** {current_q.get('hint_1')}")
        if st.session_state.hint_level >= 2:
            st.info(f"**Step 2:** {current_q.get('hint_2')}")
        if st.session_state.hint_level >= 3:
            st.success(f"**Full Solution:** {current_q.get('solution')}")
            
        if st.session_state.hint_level < 3:
            if st.button("Unlock Next Step"):
                st.session_state.hint_level += 1
                st.rerun()

# ---------------------------------------------------------
# INTERACTIVE 24/7 AI COACH (SIDEBAR/COLUMN 2)
# ---------------------------------------------------------
with col_coach:
    st.markdown("### 🤖 24/7 AI Numeracy Tutor")
    st.caption("Ask questions about any equation, conversion, or formula.")

    # High-Performance Chat Container
    chat_container = st.container(height=420)
    for chat_item in st.session_state.chat_log:
        with chat_container.chat_message(chat_item["role"]):
            st.markdown(chat_item["content"])

    user_query = st.chat_input("Ask: e.g. How do I convert 15 km/h to m/min?")
    if user_query:
        st.session_state.chat_log.append({"role": "user", "content": user_query})
        with chat_container.chat_message("user"):
            st.markdown(user_query)

        # Context-Aware Tutor Prompting
        context = f"Question Context: {current_q.get('question')} | Stimulus: {current_q.get('stimulus')}"
        tutor_system = f"""
        You are an elite, patient NCEA Numeracy tutor for students preparing for Unit Standard 32406.
        Context: {context}.
        
        MANDATORY RULES:
        1. Format ALL mathematical equations, arithmetic steps, and unit calculations strictly in **BOLD**.
        2. Use standard school symbols: '×' for multiplication and '÷' for division. NEVER use '*' or '/'.
        3. Structure responses concisely: maximum 3-4 bullet points. Always direct them on what to copy into their notebook.
        """
        try:
            bot_response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=user_query,
                config=types.GenerateContentConfig(
                    system_instruction=tutor_system
                ),
            )
            reply = bot_response.text
        except Exception:
            reply = "My neural engine is experiencing heavy load. Please refer to the **Interactive Reference Notebook** above for this formula!"

        st.session_state.chat_log.append({"role": "assistant", "content": reply})
        with chat_container.chat_message("assistant"):
            st.markdown(reply)
