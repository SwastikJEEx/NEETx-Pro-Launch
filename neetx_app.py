import streamlit as st
import random
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="NeetX Pro | NEET Prep Companion",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4CAF50;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #333;
        margin-top: 1rem;
    }
    .card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .correct {
        color: #28a745;
        font-weight: bold;
    }
    .incorrect {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- Data: Flashcards & Questions ---
BIOLOGY_CARDS = [
    {"q": "What is the powerhouse of the cell?", "a": "Mitochondria"},
    {"q": "What is the basic unit of classification?", "a": "Species"},
    {"q": "Which hormone controls blood sugar levels?", "a": "Insulin"},
    {"q": "What is the fluid mosaic model related to?", "a": "Plasma Membrane structure"},
    {"q": "Where does Glycolysis occur?", "a": "Cytoplasm"},
]

PHYSICS_CARDS = [
    {"q": "What is the SI unit of Capacitance?", "a": "Farad"},
    {"q": "Formula for Kinetic Energy?", "a": "1/2 mv²"},
    {"q": "What implies constant velocity?", "a": "Zero Net Force"},
    {"q": "Value of acceleration due to gravity (g)?", "a": "9.8 m/s²"},
    {"q": "What type of lens corrects Myopia?", "a": "Concave Lens"},
]

CHEMISTRY_CARDS = [
    {"q": "What is the pH of pure water?", "a": "7"},
    {"q": "What is the shape of the methane molecule?", "a": "Tetrahedral"},
    {"q": "Which law relates pressure and volume?", "a": "Boyle's Law"},
    {"q": "Chemical formula for laughing gas?", "a": "N₂O (Nitrous Oxide)"},
    {"q": "What is the oxidation state of O in H₂O₂?", "a": "-1"},
]

QUIZ_DATA = [
    {
        "question": "Which of the following is not a pyrimidine base?",
        "options": ["Cytosine", "Thymine", "Uracil", "Guanine"],
        "answer": "Guanine",
        "subject": "Biology"
    },
    {
        "question": "The dimension of Planck's constant is same as that of:",
        "options": ["Energy", "Momentum", "Angular Momentum", "Power"],
        "answer": "Angular Momentum",
        "subject": "Physics"
    },
    {
        "question": "Which element has the highest electronegativity?",
        "options": ["Chlorine", "Fluorine", "Oxygen", "Nitrogen"],
        "answer": "Fluorine",
        "subject": "Chemistry"
    },
    {
        "question": "In human body, which organ is responsible for filtration of blood?",
        "options": ["Heart", "Lungs", "Kidney", "Liver"],
        "answer": "Kidney",
        "subject": "Biology"
    }
]

# --- Session State Initialization ---
if 'flashcards' not in st.session_state:
    st.session_state.flashcards = BIOLOGY_CARDS + PHYSICS_CARDS + CHEMISTRY_CARDS
if 'current_card_index' not in st.session_state:
    st.session_state.current_card_index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'quiz_index' not in st.session_state:
    st.session_state.quiz_index = 0
if 'quiz_finished' not in st.session_state:
    st.session_state.quiz_finished = False
# Helper state for AI Flashcards
if 'ai_generated_cards' not in st.session_state:
    st.session_state.ai_generated_cards = []

# --- Helper Functions ---
def next_card():
    st.session_state.current_card_index = (st.session_state.current_card_index + 1) % len(st.session_state.flashcards)
    st.session_state.show_answer = False

def prev_card():
    st.session_state.current_card_index = (st.session_state.current_card_index - 1) % len(st.session_state.flashcards)
    st.session_state.show_answer = False

def toggle_answer():
    st.session_state.show_answer = not st.session_state.show_answer

def shuffle_cards():
    random.shuffle(st.session_state.flashcards)
    st.session_state.current_card_index = 0
    st.session_state.show_answer = False

def check_answer(selected_option, correct_option):
    if selected_option == correct_option:
        st.session_state.quiz_score += 1
        st.success("Correct! ✅")
    else:
        st.error(f"Wrong ❌. The correct answer was: {correct_option}")
    
    time.sleep(1) # Pause to let user see result
    
    if st.session_state.quiz_index < len(QUIZ_DATA) - 1:
        st.session_state.quiz_index += 1
    else:
        st.session_state.quiz_finished = True
    st.rerun()

def restart_quiz():
    st.session_state.quiz_score = 0
    st.session_state.quiz_index = 0
    st.session_state.quiz_finished = False
    random.shuffle(QUIZ_DATA) # Shuffle questions for new attempt
    st.rerun()

# --- Main App Layout ---

# Sidebar Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3062/3062634.png", width=80)
    st.title("NeetX Pro")
    # Added "AI Flashcards" to the menu
    menu = st.radio("Navigation", ["Dashboard", "Flashcards", "AI Flashcards", "Mock Quiz", "About"])
    
    st.markdown("---")
    st.info("💡 **Tip:** Consistency is key to cracking NEET!")

# Page Content
if menu == "Dashboard":
    st.markdown('<div class="main-header">Welcome to NeetX Pro 🚀</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Days to Exam", value="145", delta="-1 day")
    with col2:
        st.metric(label="Topics Covered", value="12/90", delta="2 this week")
    with col3:
        st.metric(label="Avg Quiz Score", value="85%", delta="+5%")
    
    st.markdown("### 📚 Subject Focus Today")
    tab1, tab2, tab3 = st.tabs(["Biology", "Physics", "Chemistry"])
    
    with tab1:
        st.markdown("**Focus:** Human Physiology")
        st.progress(65)
    with tab2:
        st.markdown("**Focus:** Optics")
        st.progress(30)
    with tab3:
        st.markdown("**Focus:** Organic Chemistry")
        st.progress(45)

elif menu == "Flashcards":
    st.markdown('<div class="main-header">⚡ Rapid Fire Flashcards</div>', unsafe_allow_html=True)
    
    # Filter selection
    subject_filter = st.selectbox("Select Subject Deck", ["All", "Biology", "Physics", "Chemistry"])
    
    # Update deck based on selection (Temporary logic for display)
    if subject_filter == "Biology":
        current_deck = BIOLOGY_CARDS
    elif subject_filter == "Physics":
        current_deck = PHYSICS_CARDS
    elif subject_filter == "Chemistry":
        current_deck = CHEMISTRY_CARDS
    else:
        current_deck = st.session_state.flashcards

    # Note: We track index globally, but if deck changes size, we need to be safe
    if st.session_state.current_card_index >= len(current_deck):
        st.session_state.current_card_index = 0
        
    card = current_deck[st.session_state.current_card_index]
    
    # Card Display UI
    col_spacer_l, col_card, col_spacer_r = st.columns([1, 2, 1])
    
    with col_card:
        st.markdown(f"""
        <div class="card">
            <h3>Card {st.session_state.current_card_index + 1} / {len(current_deck)}</h3>
            <hr>
            <h2 style="color: #2c3e50;">{card['q']}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.show_answer:
            st.markdown(f"""
            <div class="card" style="background-color: #d4edda; border: 1px solid #c3e6cb;">
                <h2 style="color: #155724;">{card['a']}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Controls
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⬅️ Previous"):
                prev_card()
        with c2:
            if st.button("👀 Show/Hide Answer"):
                toggle_answer()
        with c3:
            if st.button("Next ➡️"):
                next_card()
                
        if st.button("🔀 Shuffle Deck"):
            shuffle_cards()

elif menu == "AI Flashcards":
    st.markdown('<div class="main-header">🤖 AI Smart Flashcards</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        Generate custom flashcards instantly from any topic or your own notes.
    </div>
    """, unsafe_allow_html=True)

    with st.form("ai_flashcard_form"):
        topic_input = st.text_area("Enter Topic or Paste Notes", height=150, placeholder="e.g., Photosynthesis, Newton's Laws, or paste a paragraph from NCERT...")
        num_cards = st.slider("Number of Cards", 3, 10, 5)
        submitted = st.form_submit_button("Generate Cards ✨")
        
        if submitted and topic_input:
            with st.spinner("Analyzing text and generating questions..."):
                time.sleep(2) # Simulating API delay
                # Mock generation logic for demonstration
                new_cards = [
                    {"q": f"Question 1 about {topic_input[:20]}...", "a": "Answer based on AI analysis."},
                    {"q": f"Key concept in {topic_input[:20]}...", "a": "Detailed explanation generated by AI."},
                    {"q": "Critical thinking question...", "a": "AI derived answer."}
                ]
                st.session_state.ai_generated_cards = new_cards
                st.success("Cards Generated Successfully!")

    if st.session_state.ai_generated_cards:
        st.markdown("### 📝 Generated Cards Preview")
        for i, card in enumerate(st.session_state.ai_generated_cards):
            with st.expander(f"Q: {card['q']}"):
                st.write(f"**A:** {card['a']}")
        
        if st.button("Add to My Deck"):
            st.session_state.flashcards.extend(st.session_state.ai_generated_cards)
            st.success("Added to your main Flashcard deck!")

elif menu == "Mock Quiz":
    st.markdown('<div class="main-header">📝 Mini Mock Test</div>', unsafe_allow_html=True)
    
    if st.session_state.quiz_finished:
        st.balloons()
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background-color: #e2e3e5; border-radius: 10px;">
            <h2>Quiz Completed!</h2>
            <h1>Score: {st.session_state.quiz_score} / {len(QUIZ_DATA)}</h1>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Restart Quiz"):
            restart_quiz()
    else:
        q_data = QUIZ_DATA[st.session_state.quiz_index]
        
        st.markdown(f"**Question {st.session_state.quiz_index + 1} of {len(QUIZ_DATA)}** ({q_data['subject']})")
        st.progress((st.session_state.quiz_index) / len(QUIZ_DATA))
        
        st.markdown(f"### {q_data['question']}")
        
        cols = st.columns(2)
        for i, option in enumerate(q_data['options']):
            if cols[i % 2].button(option, key=f"opt_{i}"):
                check_answer(option, q_data['answer'])

elif menu == "About":
    st.markdown('<div class="main-header">ℹ️ About NeetX Pro</div>', unsafe_allow_html=True)
    st.markdown("""
    **NeetX Pro** is a simplified demonstration app built with Python and Streamlit to help students prepare for the National Eligibility cum Entrance Test (NEET).
    
    **Features:**
    - Topic-wise Flashcards for quick revision.
    - Interactive Mock Quizzes.
    - Study Progress Dashboard.
    
    Built for future doctors! 🩺
    """)
