cards = json.loads(content)
                            st.session_state.flashcards = cards
                            st.rerun()
                        except Exception as e:
                            st.error(f"Generation failed: {e}")

        if st.button("⚡ AI Flashcards", use_container_width=True):
            flashcard_generator_dialog()
        # ----------------------------------------------------

        # 3. Deep Research Toggle (Full width below others)
        st.toggle("🔬 Deep Research", key="deep_research_mode", help="Enable deep theoretical explanations and first-principles derivations.")
        
        if st.session_state.deep_research_mode:
            st.caption("🧐 Research Mode: ON")

        st.markdown("---")

        # --- SESSION CONTROLS ---
        if st.button("✨ New Session", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": "Fresh start! 🌟 What topic shall we tackle now?"}]
            if "thread_id" in st.session_state:
                del st.session_state.thread_id
            st.toast("Chat history cleared!", icon="🧹")
            st.session_state.flashcards = None
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

# --- 8. FLASHCARD DISPLAY LOGIC ---
if st.session_state.flashcards:
    st.markdown("### ⚡ Flashcard Session")
    components.html(get_flashcard_html(st.session_state.flashcards), height=400)
    if st.button("❌ Close Flashcards", key="close_fc"):
        st.session_state.flashcards = None
        st.rerun()
    st.markdown("---")

# --- 9. CHAT LOGIC ---
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
        
        # --- NEET SPECIALIZED INSTRUCTIONS WITH HINGLISH & HIDDEN CODE ---
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
        
        MANDATORY OPERATING RULES:
        1. **SILENT CALCULATIONS (CRITICAL):** For Physics/Chemistry numericals, use the **Code Interpreter (Python)** tool to calculate.
           - **NEVER** output the Python code, variable assignments (e.g. `L_orbital = ...`), or print statements to the user.
           - **ONLY** show the formula in LaTeX, the values substituted, and the final answer.
        
        2. **BIOLOGY = NCERT:** Strictly stick to NCERT content. Quote lines.
        
        3. **FORMATTING:** Use LaTeX ($...$ for inline, $$...$$ for block) for all math/science.
        
        4. **SEARCH:** Use internal tools to find recent cutoffs/trends if asked.
        
        5. **MOTIVATION:** If they are wrong, say "Koi baat nahi, wapas try karte hain."
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
