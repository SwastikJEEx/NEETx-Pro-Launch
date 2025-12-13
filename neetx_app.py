import streamlit as st
import time
from openai import OpenAI
import os
import re
from datetime import datetime, timedelta
from fpdf import FPDF
import requests
import traceback
import logging

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="NEETx Pro", page_icon="🧬", layout="wide", initial_sidebar_state="expanded")

# *** EMAIL SETTINGS ***
ADMIN_EMAIL = "neetxaipro@gmail.com"  

# --- 2. GLOBAL CONSTANTS ---
LOGO_PATH = "logo.jpg.png"

# --- 3. SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome Future Doctor! 🩺 Biology, Chemistry or Physics—doubt upload karo ya poocho. Let's dominate NEET! 🧬"}]
if "processing" not in st.session_state: st.session_state.processing = False
if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0
if "audio_key" not in st.session_state: st.session_state.audio_key = 0
if "current_uploaded_file" not in st.session_state: st.session_state.current_uploaded_file = None

# AUTH & REGISTRATION STATE
if "is_verified" not in st.session_state: st.session_state.is_verified = False
if "user_details" not in st.session_state: st.session_state.user_details = {}

# MODE STATES
if "ultimate_mode" not in st.session_state: st.session_state.ultimate_mode = False
if "deep_research_mode" not in st.session_state: st.session_state.deep_research_mode = False
if "mistake_analysis_mode" not in st.session_state: st.session_state.mistake_analysis_mode = False

# Simple logger
logger = logging.getLogger("neetx")
logger.setLevel(logging.INFO)

# --- 4. PROFESSIONAL DARK GREEN CSS (THEME MATCHING) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Main Background - Darker for contrast */
    .stApp { background-color: #050805 !important; color: #E0E0E0 !important; }
    [data-testid="stSidebar"] { background-color: #0A110A !important; border-right: 1px solid #1E3A1E !important; }
    header, header * { background-color: #050805 !important; color: #E0E0E0 !important; }
    
    /* Text Colors */
    h1, h2, h3, h4, h5, h6, p, li, div, span, label, a, small, strong, code { color: #E0E0E0 !important; }
    strong { color: #2ECC71 !important; font-weight: 600; } /* Neon Green Strong Text */

    /* BIGGER CHAT TEXT FOR READABILITY */
    .stChatMessage p, .stChatMessage li, .stChatMessage div {
        font-size: 1.15rem !important;
        line-height: 1.6 !important;
    }
    
    /* Inputs & Selects - Green Borders */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="base-input"] {
        background-color: #0F1C0F !important; 
        border: 1px solid #2ECC71 !important; 
        border-radius: 8px !important;
    }
    input[type="text"], input[type="password"], textarea { color: #FFFFFF !important; }
    
    /* Buttons - NEET Green Theme */
    button, .stButton>button {
        background-color: #2ECC71 !important; /* Emerald Green */
        color: #000000 !important; /* Black Text for contrast */
        border-radius: 8px !important; 
        font-weight: 700 !important;
    }
    button:hover, .stButton>button:hover { 
        background-color: #27AE60 !important; /* Darker Green on Hover */
        box-shadow: 0px 0px 10px rgba(46, 204, 113, 0.4) !important;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] { 
        background-color: #0A110A !important; 
        border: 1px solid #1E3A1E !important; 
        border-radius: 8px !important; 
    }
    
    /* Chat Input */
    .stChatInput { border-color: #2ECC71 !important; }
    
    /* Spinner/Loader Color */
    .stSpinner > div > div { border-top-color: #2ECC71 !important; }

    .block-container { padding-top: 1rem; padding-bottom: 140px; max-width: 1200px; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

# --- 5. HELPER FUNCTIONS ---

def send_lead_notification(name, email, phone):
    """Sends Lead Generation email via FormSubmit"""
    url = f"https://formsubmit.co/{ADMIN_EMAIL}"
    payload = {
        "_subject": f"🧬 NEW NEETx USER: {name}",
        "_captcha": "false", 
        "_template": "table",
        "Name": name,
        "Email": email,
        "Phone": phone,
        "Status": "Free Trial Activated",
        "Timestamp": str(datetime.now())
    }
    try:
        requests.post(url, data=payload)
        return True
    except Exception as e:
        logger.error(f"Lead send failed: {e}")
        return True

def cleanup_text_for_pdf(text):
    """Translates LaTeX and special chars to PDF-friendly text"""
    if not text: return ""
    text = re.sub(r'【.*?†source】', '', text)
    
    replacements = {
        r'\alpha': 'alpha', r'\beta': 'beta', r'\gamma': 'gamma', r'\theta': 'theta',
        r'\pi': 'pi', r'\infty': 'infinity',
        r'\le': '<=', r'\ge': '>=', r'\neq': '!=', r'\approx': '~=',
        r'\rightarrow': '->', r'\leftarrow': '<-', r'\implies': '=>',
        r'\cdot': '*', r'\times': 'x',
        r'\frac': ' frac ', r'\sqrt': 'sqrt',
        r'\int': 'Integral ', r'\sum': 'Sum ',
        '$$': '\n', '$': ''
    }
    for latex, plain in replacements.items():
        text = text.replace(latex, plain)
    text = text.replace('{', '(').replace('}', ')')
    text = text.replace('\\', '')
    return text

def clean_latex_for_chat(text):
    if not text: return ""
    text = re.sub(r'【.*?†source】', '', text)
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
    return text

def show_branding():
    # Adjusted columns for wide layout to keep logo centered
    c1, c2, c3 = st.columns([2, 2, 2])
    with c2:
        try:
            # Display Logo from local file
            st.image(LOGO_PATH, use_container_width=True)
        except: 
            # Fallback
            st.markdown(f"**NEETx PRO**")

    st.markdown("""
        <div style="text-align: center; margin-top: -15px; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 52px; font-weight: 700; letter-spacing: 1px;">
                NEETx <span style="color:#2ECC71;">PRO</span>
            </h1>
            <p style="color: #AAAAAA; font-size: 18px; margin-top: 8px;">
                Your AI Biology, Physics & Chem Tutor | <strong>Target 720/720</strong> 🩺
            </p>
        </div>
    """, unsafe_allow_html=True)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'NEETx Pro - Revision Notes', 0, 1, 'C')
        self.ln(5)
    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(46, 204, 113) # Green Color
        self.cell(0, 10, str(label), 0, 1, 'L')
        self.ln(2)
    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.set_text_color(50, 50, 50)
        self.clean = cleanup_text_for_pdf(body)
        clean = self.clean.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 7, clean)
        self.ln()

def generate_pdf(messages):
    pdf = PDF()
    pdf.add_page()
    for msg in messages:
        role = "NEETx" if msg["role"] == "assistant" else "Future_Dr"
        pdf.chapter_title(role)
        pdf.chapter_body(msg["content"])
    return pdf.output(dest='S').encode('latin-1', 'ignore')

if st.session_state.get('logout', False):
    st.session_state.clear()
    st.rerun()

# --- 6. SIDEBAR LOGIC (FREE REGISTRATION & TOOLS) ---
with st.sidebar:
    # A. IF NOT VERIFIED -> SHOW REGISTRATION FORM
    if not st.session_state.is_verified:
        st.markdown("## 🔓 Get Free Access")
        st.info("Unlock your AI Medical Coach instantly.")
        
        with st.form("signup_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            phone = st.text_input("Phone Number")
            submit_reg = st.form_submit_button("🩺 Start Free Trial")
        
        if submit_reg:
            if name and email and phone:
                with st.spinner("Activating NEETx Engine..."):
                    send_lead_notification(name, email, phone)
                    st.session_state.user_details = {"name": name, "email": email}
                    st.session_state.is_verified = True
                    st.toast(f"Welcome, {name}! Let's study.", icon="🚀")
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("⚠️ Please fill in all details.")
    
    # B. IF VERIFIED -> SHOW TOOLS
    else:
        st.markdown(f"👤 **{st.session_state.user_details.get('name', 'Doctor')}**")
        st.success("✅ NEETx Pro Active")
        st.markdown("---")
        
        # --- NEW FEATURES: NEETX ULTIMATE & TOOLS ---
        st.markdown("### ⚡ Power Tools")
        
        # 1. NEETx Ultimate Toggle
        st.toggle("🔥 NEETx Ultimate", key="ultimate_mode", help="Unlock advanced problem solving and deep conceptual analysis.")
        
        if st.session_state.ultimate_mode:
            st.caption("🚀 Advanced Mode: ON")
        
        # 2. Tools Buttons (Layout in columns)
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            if st.button("📚 Formulas", use_container_width=True):
                 st.toast("Formula Sheet Mode: Ask for any chapter!", icon="📐")
                 st.session_state.messages.append({"role": "assistant", "content": "I'm ready! Which chapter's **Formula Sheet** do you need? (e.g., Electrostatics, Genetics)"})
                 st.rerun()
        with col_t2:
            if st.button("📝 Mock Test", use_container_width=True):
                st.toast("Mock Test Initialized...", icon="⏳")
                st.session_state.messages.append({"role": "assistant", "content": "Let's test your prep! 🎯 Topic batao, I'll generate a **Mini Mock Test** with 5 tough questions."})
                st.rerun()
        
        # 3. Mistake Analyzer (Placed BELOW buttons)
        st.toggle("⚠️ Mistake Analyzer", key="mistake_analysis_mode", help="AI actively hunts for your logic errors.")
        
        if st.session_state.mistake_analysis_mode:
            st.caption("🔍 Analyzer: Active")

        # 4. Deep Research Toggle (Placed BELOW buttons & Analyzer)
        st.toggle("🔬 Deep Research", key="deep_research_mode", help="Enable deep theoretical explanations and first-principles derivations.")
        
        if st.session_state.deep_research_mode:
            st.caption("🧐 Research Mode: ON")

        st.markdown("---")

        # --- SESSION CONTROLS ---
        if st.button("✨ New Session", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": "Fresh start! 🌟 What topic shall we tackle now?"}]
            # Reset thread ID to force a new context (if you want fresh context)
            if "thread_id" in st.session_state:
                del st.session_state.thread_id
            st.toast("Chat history cleared!", icon="🧹")
            st.rerun()
        
        st.markdown("**📎 Attach Question**")
        
        # File Uploader Logic
        if st.session_state.processing:
            if st.session_state.current_uploaded_file:
                st.markdown("**Attachment (locked):**")
                st.markdown(f"📄 *{getattr(st.session_state.current_uploaded_file, 'name', 'file')}*")
            else:
                st.markdown("_Locked while answering._")
        else:
            uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "pdf"], key=f"uploader_{st.session_state.uploader_key}", label_visibility="collapsed")
            if uploaded_file:
                st.session_state.current_uploaded_file = uploaded_file
            
            if st.session_state.current_uploaded_file:
                if st.button("Remove attachment"):
                    st.session_state.current_uploaded_file = None
                    st.session_state.uploader_key += 1
                    st.rerun()
        
        st.markdown("**🎙️ Voice Chat**")
        audio_value = st.audio_input("Speak", key=f"audio_{st.session_state.audio_key}", label_visibility="collapsed")
        st.markdown("---")
        
        if len(st.session_state.messages) > 1:
            pdf_bytes = generate_pdf(st.session_state.messages)
            st.download_button("📥 Download Notes", data=pdf_bytes, file_name="NEETx_Notes.pdf", mime="application/pdf", use_container_width=True)
        
        if st.button("Logout", use_container_width=True): 
            st.session_state['logout'] = True
            st.rerun()

    # --- CONTACT US DROPDOWN ---
    st.markdown("---")
    with st.expander("📞 Contact Us"):
        st.write("**Email:** neetxaipro@gmail.com")
        st.write("**WhatsApp:** +91 9839940400")
    
    # --- TERMS & CONDITIONS DROPDOWN ---
    with st.expander("📄 Terms & Conditions"):
        st.markdown("""
        **1. Medical Advice Disclaimer**
        NEETx PRO is an educational tool for Physics, Chemistry, and Biology. It is NOT a medical device and should not be used for medical diagnosis.

        **2. AI Accuracy**
        While optimized for NCERT and NEET patterns, AI can make mistakes. Always verify critical data with your NCERT textbooks.

        **3. Usage Policy**
        For personal preparation use only. Sharing accounts is prohibited.
        """, unsafe_allow_html=True)

# --- 7. MAIN INTERFACE ---
show_branding()

# If not verified, show landing teaser and stop
if not st.session_state.is_verified:
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #0A110A; padding: 25px; border-radius: 12px; border-left: 5px solid #2ECC71; text-align: center; margin-bottom: 30px;">
        <h3 style="color: #FFFFFF; margin:0;">👋 Welcome to NEETx PRO</h3>
        <p style="color: #AAAAAA; margin-top: 10px;">
            The ultimate AI tool for NEET UG Aspirants.<br>
            <strong>Use the Sidebar on the left to Register for FREE access!</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- NEET SPECIALIZED FEATURES ---
    c1, c2 = st.columns(2)
    with c1:
        st.info("**🧬 NCERT Biology Mastery**\n\nDeep understanding of every line of NCERT. We explain diagrams and theory instantly.")
        st.info("**🧪 Organic & Inorganic Wizard**\n\nLearn reactions, exceptions, and mechanisms with clear steps.")
        st.info("**🧘 Stress & Strategy**\n\nNot just studies—we help you manage exam pressure and build a winning mindset.")
    with c2:
        st.info("**👁️ Vision Intelligence**\n\nClick a photo of any diagram or question. We solve it instantly.")
        st.info("**➗ Physics Simplified**\n\nStruggling with calculations? We break down numericals into simple steps.")
        st.info("**⚡ Rank Dominance**\n\nStrategies used by Toppers to score 700+. Beat the competition.")
    st.stop()

# --- 8. CHAT LOGIC ---
try:
    # ------------------------------------------------------------------
    # IMPORTANT: ADD YOUR KEYS TO .streamlit/secrets.toml for security!
    # Or replace st.secrets calls below with the keys you provided.
    # ------------------------------------------------------------------
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    assistant_id = st.secrets["ASSISTANT_ID"]
except Exception as e:
    st.error("🚨 System Error: OpenAI Keys missing. Please add them to secrets.toml")
    st.stop()

if "thread_id" not in st.session_state:
    try:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
    except:
        st.error("Connection error. Please refresh.")
        st.stop()

# Handle Audio Input
audio_prompt = None
if 'audio_value' in locals() and audio_value and not st.session_state.processing:
    with st.spinner("🎧 Listening..."):
        try:
            transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_value, language="en")
            audio_prompt = transcription.text
        except:
            pass

# Handle Text Input
text_prompt = st.chat_input("Ask a doubt (Biology, Phy, Chem)...", disabled=st.session_state.processing)
prompt = audio_prompt if audio_prompt else text_prompt

if prompt:
    st.session_state.processing = True
    msg_data = {"role": "user", "content": prompt}
    
    if st.session_state.current_uploaded_file:
        uf = st.session_state.current_uploaded_file
        msg_data.update({"file_data": uf.getvalue(), "file_name": getattr(uf, "name", "file"), "file_type": getattr(uf, "type", "")})
            
    st.session_state.messages.append(msg_data)
    st.rerun()

# Display Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=LOGO_PATH if msg["role"]=="assistant" else "🧑‍⚕️"):
        if "file_data" in msg:
            if str(msg["file_type"]).startswith("image"): st.image(msg["file_data"], width=200)
            else: st.markdown(f"📄 *{msg.get('file_name')}*")
        st.markdown(clean_latex_for_chat(msg["content"]))

# Generate Response
if st.session_state.processing and st.session_state.messages[-1]["role"] == "user":
    msg_text = st.session_state.messages[-1]["content"]
    api_content = [{"type": "text", "text": msg_text}]
    att = []
    
    # Handle File Attachment
    uploaded_file_obj = st.session_state.current_uploaded_file
    if uploaded_file_obj:
        try:
            tfile = f"temp_{getattr(uploaded_file_obj, 'name', 'file')}"
            with open(tfile, "wb") as f: f.write(uploaded_file_obj.getbuffer())
            fres = client.files.create(file=open(tfile, "rb"), purpose="assistants")
            
            if uploaded_file_obj.type == "application/pdf":
                att.append({"file_id": fres.id, "tools": [{"type": "code_interpreter"}]})
            else:
                api_content.append({"type": "image_file", "image_file": {"file_id": fres.id}})
            
            try: os.remove(tfile)
            except: pass
        except:
            pass 
    
    try:
        client.beta.threads.messages.create(thread_id=st.session_state.thread_id, role="user", content=api_content, attachments=att if att else None)
        
        # --- ENHANCED NEETx INSTRUCTIONS (Structure imported from JEEx but tailored for NEET) ---
        base_instructions = """
        You are NEETx, an elite AI Tutor for NEET UG aspirants.
        
        ERROR_HANDLING_AND_SCOPE:
        1. **STRICT DOMAIN BOUNDARY**: Your knowledge is strictly limited to Physics, Chemistry, and Biology relevant to NEET UG.
        2. **IRRELEVANT TOPICS**: If the user asks about topics NOT related to NEET (e.g., general coding, politics, movies, cooking, dating, sports, general news):
           - **Action**: Provide a VERY BRIEF (maximum 1 sentence) factual definition of the topic to be polite.
           - **Pivot**: Immediately pivot back to NEET preparation, reminding them of the goal (White Coat/MBBS).
           - **Redirect**: Ask a relevant question to bring them back.
           - **Example**: User: "Who won the cricket match?" -> Bot: "India won the match. But Future Doctor, distractions won't get us to AIIMS. Let's focus on Genetics?"
        
        YOUR PERSONA:
        - **Role:** Senior Medical Student Mentor.
        - **Language:** **Hinglish** (Mix of English & Hindi). Use phrases like "Dekho future doctor," "Ye concept important hai," "Samjhe?".
        - **Tone:** Encouraging, Disciplined, and Friendly.
        
        CORE CAPABILITIES:
        1. **Deep NEET Knowledge Base**: Simulate an internet search by cross-referencing your internal database of NEET PYQs, NCERT nuances, and recent exam trends.
        2. **Search Engine Behavior**: When asked about specific data (e.g., "Cutoff for AIIMS Delhi"), use your internal knowledge to provide the most recent accurate estimates.
        
        MANDATORY OPERATING RULES:
        1. **SILENT CALCULATIONS (CRITICAL):** For Physics/Chemistry numericals, use the **Code Interpreter (Python)** tool to calculate.
           - **NEVER** output the Python code to the user.
           - **ONLY** show the formula in LaTeX, the values substituted, and the final answer.
        2. **BIOLOGY = NCERT**: Strictly stick to NCERT content. Quote lines.
        3. **FORMATTING:** Use LaTeX ($...$ for inline, $$...$$ for block) for all math/science.
        4. **MOTIVATION:** If they are wrong, say "Koi baat nahi, wapas try karte hain."
        """

        # NEETx ULTIMATE INJECTION
        if st.session_state.ultimate_mode:
            base_instructions += """
            \n\n*** ULTRA MODE ACTIVATED ***
            The user has enabled 'NEETx Ultimate'. 
            1. INCREASE COMPLEXITY: Assume the user is aiming for Rank 1 (720/720).
            2. INTER-LINKING: Actively connect concepts (e.g., Genetics + Evolution, Electrostatics + Gravitation).
            3. TRICKY QUESTIONS: Focus on assertion-reasoning and statement-based questions common in recent NEET exams.
            4. TONE: Highly focused, rigorous, and demanding.
            """

        # MISTAKE ANALYSIS INJECTION (NEW FEATURE)
        if st.session_state.mistake_analysis_mode:
            base_instructions += """
            \n\n*** MISTAKE ANALYSIS MODE: CRITICAL ***
            The user wants to find errors in their logic.
            1. Analyze the user's question/solution for conceptual gaps, sign errors, or calculation mistakes.
            2. If the user presents a solution, DO NOT just give the right answer. First, explicitly state: "Here is where you went wrong: [Explain Error]".
            3. Then, provide the correct derivation or biological mechanism.
            4. Be strict but constructive. Identify if the error is Conceptual (Logic) or Silly (Calculation).
            """

        # DEEP RESEARCH INJECTION
        if st.session_state.deep_research_mode:
            base_instructions += """
            \n\n*** DEEP RESEARCH MODE ACTIVATED ***
            1. EXPLAIN LIKE A SCIENTIST: The user wants deep theoretical understanding beyond rote memorization.
            2. FIRST PRINCIPLES: Explain the 'why' behind biological mechanisms and physical laws.
            3. DEPTH OVER BREADTH: Go deep into the underlying mechanisms.
            """
        
        with st.chat_message("assistant", avatar=LOGO_PATH):
            stream = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id, assistant_id=assistant_id, stream=True,
                additional_instructions=base_instructions,
                tools=[{"type": "code_interpreter"}]
            )
            resp = st.empty()
            full_text = ""
            
            for event in stream:
                if event.event == "thread.message.delta":
                    for c in event.data.delta.content:
                        if c.type == "text":
                            full_text += c.text.value
                            resp.markdown(clean_latex_for_chat(full_text) + "▌")
            
            resp.markdown(clean_latex_for_chat(full_text))
            st.session_state.messages.append({"role": "assistant", "content": full_text})
            
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": "⚠️ Network issue. Please try again."})
    
    st.session_state.current_uploaded_file = None
    st.session_state.uploader_key += 1
    if 'audio_value' in locals() and audio_value: st.session_state.audio_key += 1
    st.session_state.processing = False
    st.rerun()
