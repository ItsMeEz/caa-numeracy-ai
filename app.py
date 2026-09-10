import json
import os
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="NZQA English Examination Machine",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# HIGH-CONTRAST PRODUCTION DESIGN SYSTEM
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { background-color: #090d16; color: #f1f5f9; }
    
    .hud-card {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        border: 2px solid #334155;
        border-radius: 14px;
        padding: 18px 24px;
        margin-bottom: 20px;
    }
    .hud-metric-label { font-size: 0.72rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
    .hud-metric-val { font-size: 1.25rem; font-weight: 800; color: #38bdf8; }

    .scenario-card {
        background: #0d1527;
        border-left: 6px solid #38bdf8;
        border-radius: 10px;
        padding: 18px 22px;
        margin: 16px 0;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    .exemplar-box {
        background: #030712;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 14px 18px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.88rem;
        line-height: 1.6;
        color: #cbd5e1;
    }
    
    .grade-badge-e { background: rgba(168, 85, 247, 0.2); border: 2px solid #a855f7; color: #d8b4fe; font-weight: 800; padding: 4px 12px; border-radius: 6px; }
    .grade-badge-m { background: rgba(56, 189, 248, 0.2); border: 2px solid #38bdf8; color: #7dd3fc; font-weight: 800; padding: 4px 12px; border-radius: 6px; }
    .grade-badge-a { background: rgba(34, 197, 94, 0.2); border: 2px solid #22c55e; color: #86efac; font-weight: 800; padding: 4px 12px; border-radius: 6px; }
    .grade-badge-n { background: rgba(239, 68, 68, 0.2); border: 2px solid #ef4444; color: #fca5a5; font-weight: 800; padding: 4px 12px; border-radius: 6px; }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# CLIENT & ENVIRONMENT INITIALIZATION
# -----------------------------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("🔑 GEMINI_API_KEY is missing. Please configure it in Streamlit Secrets.")
    st.stop()

@st.cache_resource
def get_ai_client(key: str):
    return genai.Client(api_key=key)

client = get_ai_client(api_key)

# -----------------------------------------------------------------------------
# BENCHMARK EXEMPLAR DATASET (NZQA STANDARDS AS91099 & AS91098)
# -----------------------------------------------------------------------------
EXEMPLAR_BANK = {
    "AS91099: V for Vendetta": {
        "formula": "TAKO (Intro) + SERQEL (Body)",
        "rubric": {
            "Achieved": "Describes visual techniques (lighting, camera work) and straightforwardly explains the director's purpose.",
            "Merit": "Convincingly analyses how visual/oral techniques work together to highlight consequences of state control and fear.",
            "Excellence": "Perceptively evaluates how McTeigue uses dystopian conventions to challenge contemporary real-world authoritarianism and human passivity."
        },
        "scenarios": [
            "Analyse how visual techniques create an atmosphere of dread to reinforce an important warning.",
            "Analyse how a character's transformation conveys the director's central philosophical message.",
            "Analyse how the director portrays the conflict between individual autonomy and state surveillance."
        ]
    },
    "AS91098: Harrison Bergeron": {
        "formula": "TAKO (Intro) + SWEETS (Body)",
        "rubric": {
            "Achieved": "Identifies key literary techniques (symbolism of handicaps, satire) and straightforwardly describes their meaning.",
            "Merit": "Convincingly analyses how Vonnegut's satire exposes the dangers of state-mandated conformity and suppressed intellect.",
            "Excellence": "Perceptively discusses how the text serves as a timeless warning against confusing equal opportunity with forced equality of outcome."
        },
        "scenarios": [
            "Analyse how symbolism is used to communicate a warning about the future of society.",
            "Analyse how the author uses satire to critique a commonly accepted societal value.",
            "Analyse how an extreme conflict highlights the consequences of institutional oppression."
        ]
    }
}

# -----------------------------------------------------------------------------
# SESSION PERSISTENCE & LEARNER PROFILE
# -----------------------------------------------------------------------------
DEFAULTS = {
    "standard": "AS91099: V for Vendetta",
    "active_scenario": None,
    "scaffold_mode": "Guided Scaffold (Cloze)",
    "evaluation_history": [],
    "mastery_score": 50,
    "last_eval": None
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------------------------------------------------------------
# SIDEBAR: MACHINE CONFIGURATION & PERFORMANCE TRACKER
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ Engine Configuration")
    chosen_std = st.selectbox("Active NZQA Standard:", list(EXEMPLAR_BANK.keys()))
    if chosen_std != st.session_state.standard:
        st.session_state.standard = chosen_std
        st.session_state.active_scenario = None
        st.rerun()

    st.session_state.scaffold_mode = st.radio(
        "Scaffolding Level:",
        ["Guided Scaffold (Cloze)", "Open Essay Examination"]
    )
    
    st.divider()
    st.markdown("### 📈 Neural Progress Matrix")
    st.metric("Learner Mastery Rating", f"{st.session_state.mastery_score} / 100")
    
    st.markdown("#### Official NZQA Marking Criteria:")
    rubric_info = EXEMPLAR_BANK[st.session_state.standard]["rubric"]
    st.markdown(f"**Achieved:** {rubric_info['Achieved']}")
    st.markdown(f"**Merit:** {rubric_info['Merit']}")
    st.markdown(f"**Excellence:** {rubric_info['Excellence']}")

# Pick scenario if not active
if not st.session_state.active_scenario:
    st.session_state.active_scenario = EXEMPLAR_BANK[st.session_state.standard]["scenarios"][0]

# -----------------------------------------------------------------------------
# MAIN ARENA
# -----------------------------------------------------------------------------
current_std = st.session_state.standard
std_meta = EXEMPLAR_BANK[current_std]

st.markdown(f"""
<div class="hud-card">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div class="hud-metric-label">{current_std}</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #fff;">Automated Diagnostic Essay Engine</div>
        </div>
        <div>
            <div class="hud-metric-label">Structural Formula Required</div>
            <div class="hud-metric-val">{std_meta['formula']}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Scenario Selector & Regeneration Row
col_scene, col_btn = st.columns([3.5, 1])
with col_scene:
    st.markdown(f"""
    <div class="scenario-card">
        <strong style="color: #38bdf8; text-transform: uppercase; font-size: 0.8rem; display: block; margin-bottom: 4px;">🎯 Targeted Exam Prompt:</strong>
        {st.session_state.active_scenario}
    </div>
    """, unsafe_allow_html=True)
with col_btn:
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    if st.button("🎲 Generate Fresh Prompt", use_container_width=True):
        st.session_state.active_scenario = random.choice(
            [s for s in std_meta["scenarios"] if s != st.session_state.active_scenario]
        )
        st.session_state.last_eval = None
        st.rerun()

# -----------------------------------------------------------------------------
# WORKSPACE: GUIDED CLOZE vs. OPEN ESSAY WRITER
# -----------------------------------------------------------------------------
st.markdown("### ✍️ Student Submission Workspace")

essay_text = ""

if st.session_state.scaffold_mode == "Guided Scaffold (Cloze)":
    if "V for Vendetta" in current_std:
        st.caption("Construct your **TAKO** Intro and **SERQEL** Body Paragraph using the structural blanks below:")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            tako_t = st.text_input("Title & Director (T & A):", value="In the dystopian film V for Vendetta, directed by James McTeigue,")
            tako_k = st.text_input("Keywords Linking to Prompt (K):", placeholder="the director explores how fear is used to establish totalitarian control...")
        with col_t2:
            tako_o1 = st.text_input("Techniques Outlined (O1):", value="through deliberate chiaroscuro lighting and symbolic costuming.")
            tako_o2 = st.text_input("Director's Purpose (O2):", placeholder="warning modern viewers that trading freedom for security leads to tyranny.")
            
        st.markdown("**SERQEL Body Paragraph:**")
        serq_s = st.text_input("Statement (S):", value="One primary way McTeigue portrays Norsefire's oppressive control is through visual framing.")
        serq_er = st.text_input("Evidence & Reference Scene (E & R):", placeholder="In the interrogation sequence inside the fake Larkhill prison cell...")
        serq_q = st.text_input("Quote / Visual Technique (Q):", placeholder="McTeigue employs high-contrast chiaroscuro lighting and extreme low angles...")
        serq_el = st.text_area("Effect on Audience & Society Link (E & L):", placeholder="This evokes a feeling of claustrophobia and helplessness in the viewer, illustrating how totalitarian regimes exploit human vulnerability and passive silence...")
        
        essay_text = f"{tako_t} {tako_k} {tako_o1} {tako_o2}\n\n{serq_s} {serq_er} {serq_q} {serq_el}"
        
    else:
        st.caption("Construct your **TAKO** Intro and **SWEETS** Body Paragraph using the structural blanks below:")
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            wtako_t = st.text_input("Title & Author (T & A):", value="In the satirical short story 'Harrison Bergeron', written by Kurt Vonnegut,")
            wtako_k = st.text_input("Keywords Linking to Prompt (K):", placeholder="the text critiques the destructive nature of enforced equality...")
        with col_w2:
            wtako_o1 = st.text_input("Techniques Outlined (O1):", value="through the symbolism of physical handicaps and jarring auditory imagery.")
            wtako_o2 = st.text_input("Author's Warning (O2):", placeholder="warning society that suppressing excellence eliminates genuine individuality.")
            
        st.markdown("**SWEETS Body Paragraph:**")
        sw_s = st.text_input("Statement (S):", value="Vonnegut uses severe physical handicaps to symbolise state oppression.")
        sw_w = st.text_input("Where in Text (W):", placeholder="In the Bergeron living room as George and Hazel watch the broadcast...")
        sw_e = st.text_input("Evidence / Quote (E):", placeholder='George carries "forty-seven pounds of birdshot" padlocked around his neck...')
        sw_ts = st.text_area("Technique Explanation & Society Link (T & S):", placeholder="This auditory imagery and symbolism demonstrate that suppressing critical thought reduces human civilization to the lowest common denominator...")
        
        essay_text = f"{wtako_t} {wtako_k} {wtako_o1} {wtako_o2}\n\n{sw_s} {sw_w} {sw_e} {sw_ts}"

    with st.expander("👁️ Review Compiled Output Before Grading"):
        st.code(essay_text, language="text")

else:
    st.caption("Write your full essay directly below. Ensure you include an introduction (TAKO) and at least one analytical body paragraph.")
    essay_text = st.text_area(
        "Your Essay Response:",
        height=300,
        placeholder="Type your response here. Aim for thorough integration of techniques, evidence, and universal societal links..."
    )

# -----------------------------------------------------------------------------
# HIGH-PRECISION NZQA GRADING CONTROLLER
# -----------------------------------------------------------------------------
if st.button("⚖️ Run Official NZQA Diagnostic Marking", type="primary", use_container_width=True):
    if len(essay_text.strip()) < 80:
        st.warning("⚠️ Submission is too brief to mark reliably against Level 1 NZQA standards. Provide a complete paragraph.")
    else:
        with st.spinner("🔍 Analysing against NZQA exemplar rubrics and marker benchmarks..."):
            evaluation_prompt = f"""
            You are an official NZQA English Marker evaluating a student response for New Zealand NCEA Standard: {current_std}.
            
            OFFICIAL EXAM PROMPT:
            "{st.session_state.active_scenario}"
            
            STUDENT SUBMISSION:
            \"\"\"{essay_text}\"\"\"
            
            STANDARDS MATRIX:
            - Not Achieved (N1 - N2): Lacks understanding of technique, purely plot summary, no coherent structure.
            - Achieved (A3 - A4): Straightforward identification of techniques (lighting, camera, symbolism, quotes), clear description of purpose.
            - Merit (M5 - M6): Convincing analysis of HOW visual/written techniques work together. Clear, convincing link to wider human nature / real-world society.
            - Excellence (E7 - E8): Perceptive, insightful evaluation showing sophisticated understanding of the text's enduring societal critique or universal human condition.
            
            REQUIRED STRUCTURAL CRITERIA:
            - Introduction must follow TAKO (Title, Author/Director, Key words of prompt, Outline of techniques/purpose).
            - Body must follow SERQEL (Visual) or SWEETS (Written).
            
            OUTPUT SPECIFICATION:
            Return strictly a valid JSON object without markdown formatting, code fences, or extraneous text:
            {{
                "grade": "One of: Not Achieved | Achieved | Merit | Excellence",
                "score_code": "e.g., N2, A4, M6, or E8",
                "verdict_summary": "One punchy sentence summarising the result.",
                "tako_check": "Detailed feedback on Title, Author, Key words, and Outline.",
                "body_check": "Detailed feedback on Techniques, Evidence/Quotes, and Structural Analysis.",
                "society_link_check": "Detailed evaluation of whether the submission connected to the real world or human condition.",
                "next_action_step": "The exact step the student must take to advance to the next grade tier."
            }}
            """
            
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=evaluation_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2
                    )
                )
                
                result = json.loads(response.text)
                st.session_state.last_eval = result
                
                # Dynamic model learning / score adjustment
                if "Excellence" in result["grade"]:
                    st.session_state.mastery_score = min(100, st.session_state.mastery_score + 15)
                elif "Merit" in result["grade"]:
                    st.session_state.mastery_score = min(100, st.session_state.mastery_score + 8)
                elif "Achieved" in result["grade"]:
                    st.session_state.mastery_score = min(100, st.session_state.mastery_score + 3)
                else:
                    st.session_state.mastery_score = max(10, st.session_state.mastery_score - 5)
                    
            except Exception as e:
                st.error(f"Examination Engine Error: {e}")

# -----------------------------------------------------------------------------
# DIAGNOSTIC FEEDBACK REPORT DISPLAY
# -----------------------------------------------------------------------------
if st.session_state.last_eval:
    ev = st.session_state.last_eval
    grade = ev.get("grade", "Not Achieved")
    
    badge_style = (
        "grade-badge-e" if "Excellence" in grade
        else "grade-badge-m" if "Merit" in grade
        else "grade-badge-a" if "Achieved" in grade
        else "grade-badge-n"
    )

    st.markdown("---")
    st.markdown(f"""
    <div style="background: #0f172a; border: 2px solid #334155; border-radius: 12px; padding: 20px; margin-top: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span class="{badge_style}" style="font-size: 1.1rem;">
                Official Grade: {grade} ({ev.get('score_code', 'N/A')})
            </span>
            <span style="color: #94a3b8; font-size: 0.85rem; font-weight: 700;">NZQA Level 1 Calibration</span>
        </div>
        <h4 style="color: #fff; margin-top: 4px;">{ev.get('verdict_summary')}</h4>
    </div>
    """, unsafe_allow_html=True)

    col_diag1, col_diag2 = st.columns(2)
    with col_diag1:
        st.markdown("#### 🏛️ TAKO Structural Diagnosis")
        st.info(ev.get("tako_check", "No data provided."))
        
        st.markdown("#### 🔍 Evidence & Technique Integration")
        st.info(ev.get("body_check", "No data provided."))

    with col_diag2:
        st.markdown("#### 🌍 Universal / Societal Link (Merit & Excellence Barrier)")
        st.info(ev.get("society_link_check", "No data provided."))

        st.markdown("#### 🚀 Target Action Step to Level Up")
        st.success(ev.get("next_action_step", "No data provided."))
