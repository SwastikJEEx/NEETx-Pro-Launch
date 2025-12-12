import streamlit as st
import google.generativeai as genai
import json
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="NEETx - AI Learning Assistant",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for NEETx Theme & Flashcard Animation ---
st.markdown("""
<style>
    /* NEETx Color Theme */
    .stApp {
        background-color: #f0fdf4;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Chat Styling */
    .stChatMessage {
        background-color: white;
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .stChatMessage[data-testid="stChatMessageAvatarUser"] {
        background-color: #059669; /* Emerald 600 */
    }
    
    /* Custom Button Styling */
    div.stButton > button {
        background-color: #059669;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 500;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #047857;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Input Styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
    }

    /* Modal/Expander Styling */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# --- Constants & Syllabus Data ---
NEET_SYLLABUS = {
    "Physics": [
        "Physical World and Measurement", "Kinematics", "Laws of Motion", "Work, Energy and Power",
        "Motion of System of Particles", "Gravitation", "Properties of Bulk Matter", "Thermodynamics",
        "Oscillations and Waves", "Electrostatics", "Current Electricity", "Magnetic Effects of Current",
        "Magnetism", "Electromagnetic Induction", "Alternating Currents", "Electromagnetic Waves",
        "Optics", "Dual Nature of Matter", "Atoms and Nuclei", "Electronic Devices"
    ],
    "Chemistry": [
        "Some Basic Concepts of Chemistry", "Structure of Atom", "Classification of Elements",
        "Chemical Bonding", "States of Matter", "Thermodynamics", "Equilibrium", "Redox Reactions",
        "Hydrogen", "s-Block Elements", "p-Block Elements", "Organic Chemistry - Basic Principles",
        "Hydrocarbons", "Environmental Chemistry", "Solid State", "Solutions", "Electrochemistry",
        "Chemical Kinetics", "Surface Chemistry", "Coordination Compounds", "Haloalkanes and Haloarenes",
        "Alcohols, Phenols and Ethers", "Aldehydes, Ketones and Carboxylic Acids", "Amines", "Biomolecules",
        "Polymers", "Chemistry in Everyday Life"
    ],
    "Biology": [
        "Diversity in Living World", "Structural Organisation in Animals and Plants", "Cell Structure and Function",
        "Plant Physiology", "Human Physiology", "Reproduction", "Genetics and Evolution",
        "Biology and Human Welfare", "Biotechnology and Its Applications", "Ecology and Environment"
    ]
}

MOCK_FLASHCARDS = [
    {"front": "What is the unit of Electric Field?", "back": "Newton per Coulomb (N/C) or Volt per meter (V/m)"},
    {"front": "Define Osmosis.", "back": "Movement of solvent molecules from lower solute concentration to higher solute concentration through a semi-permeable membrane."},
    {"front": "General formula of Alkanes?", "back": "CnH2n+2"},
    {"front": "Who is the father of Genetics?", "back": "Gregor Mendel"},
    {"front": "Value of Universal Gravitational Constant (G)?", "back": "6.674 × 10⁻¹¹ N·m²/kg²"}
]

# --- Helper Functions ---

def generate_flashcards(subject, chapters, level, count):
    """
    Generates flashcards using Gemini API or falls back to mock data.
    """
    api_key = ""  # Set your API Key here if you have one.
    
    if not api_key:
        time.sleep(1.5) # Simulate delay
        return MOCK_FLASHCARDS[:count]

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        
        prompt = f"""
        Generate {count} flashcards for NEET (Indian Medical Entrance Exam).
        Subject: {subject}
        Topics: {', '.join(chapters)}
        Difficulty: {level}
        
        Return ONLY a valid JSON array of objects. Each object must have exactly two keys: "front" (the question) and "back" (the answer).
        Do not include markdown code blocks. Just the raw JSON string.
        """
        
        response = model.generate_content(prompt)
        text = response.text
        
        # Clean markdown
        if text.startswith('
