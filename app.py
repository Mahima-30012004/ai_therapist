import streamlit as st
from textblob import TextBlob
import pandas as pd
import random
from fpdf import FPDF
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
from datetime import datetime
import sqlite3
import hashlib

# --- 1. BACKEND DATABASE ENGINE ---
def init_db():
    conn = sqlite3.connect('mindcare_backend.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS goals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, goal_text TEXT, status TEXT, date TEXT)''')
    conn.commit()
    conn.close()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password, hashed_text): return hashed_text if make_hashes(password) == hashed_text else False

def add_user(username, password):
    conn = sqlite3.connect('mindcare_backend.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users(username,password) VALUES (?,?)', (username, make_hashes(password)))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def login_user(username, password):
    conn = sqlite3.connect('mindcare_backend.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username =?', (username,))
    data = c.fetchone()
    conn.close()
    return check_hashes(password, data[0]) if data else False

def add_goal(username, goal):
    conn = sqlite3.connect('mindcare_backend.db')
    c = conn.cursor()
    c.execute('INSERT INTO goals (username, goal_text, status, date) VALUES (?, ?, ?, ?)', (username, goal, "Pending", datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

def get_goals(username):
    conn = sqlite3.connect('mindcare_backend.db')
    c = conn.cursor()
    c.execute('SELECT id, goal_text, status FROM goals WHERE username = ?', (username,))
    data = c.fetchall()
    conn.close()
    return data

def delete_goal(goal_id):
    conn = sqlite3.connect('mindcare_backend.db')
    c = conn.cursor()
    c.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
    conn.commit()
    conn.close()

init_db()

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="MindCare India", page_icon="🧠", layout="wide")
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = ""

# --- 3. LANGUAGE DICTIONARY ---
LANG_DICT = {
    "English": {
        "title": "MindCare India 🧠", "chat_tab": "💬 Assistant", "phq_tab": "📊 PHQ-9 Check", "breath_tab": "🧘 Breathing Space", "cloud_tab": "📈 Progress & Goals",
        "emergency": "Emergency Support Lines:", "kolkata_help": "Kolkata Helpline: 033-24637401", "submit_btn": "Submit Assessment",
        "details_header": "Patient Details", "name_label": "Full Name", "age_label": "Age", "gender_label": "Gender", "gender_options": ["Male", "Female", "Other", "Prefer not to say"],
        "q_list": ["Little interest in things", "Feeling down/hopeless", "Sleep issues", "Low energy", "Appetite issues", "Feeling like a failure", "Concentration trouble", "Slow/restless", "Thoughts of self-harm"],
        "responses": {"greetings": ["Hello! How can I help you today?", "Namaste! How are you feeling?", "Hi! I'm here to listen and help."]}
    },
    "Hindi": { "title": "माइंडकेयर इंडिया 🧠", "chat_tab": "💬 सहायक", "phq_tab": "📊 जांच", "breath_tab": "🧘 सांस", "cloud_tab": "📈 लक्ष्य", "emergency": "सहायता:", "kolkata_help": "कोलकाता: 033-24637401", "submit_btn": "जमा करें", "details_header": "विवरण", "name_label": "नाम", "age_label": "आयु", "gender_label": "लिंग", "gender_options": ["पुरुष", "महिला", "अन्य"], "q_list": ["रुचि की कमी", "उदासी", "नींद", "थकान", "भूख", "असफलता", "एकाग्रता", "सुस्ती", "आत्म-नुकसान"], "responses": {"greetings": ["नमस्ते! मैं आपकी क्या मदद कर सकता हूँ?"]} },
    "Bengali": { "title": "মাইন্ডকেয়ার ইন্ডিয়া 🧠", "chat_tab": "💬 সহায়ক", "phq_tab": "📊 পরীক্ষা", "breath_tab": "🧘 ব্যায়াম", "cloud_tab": "📈 লক্ষ্য", "emergency": "সহায়তা:", "kolkata_help": "কলকাতা: ০৩৩-২৪৬৩৭৪০১", "submit_btn": "জমা দিন", "details_header": "তথ্য", "name_label": "নাম", "age_label": "বয়স", "gender_label": "লিঙ্গ", "gender_options": ["পুরুষ", "মহিলা", "অন্যান্য"], "q_list": ["আগ্রহের অভাব", "মন খারাপ", "ঘুমের সমস্যা", "ক্লান্তি", "খিদে", "ব্যর্থতা", "মনোযোগ", "ধীরে চলা", "ক্ষতি করার চিন্তা"], "responses": {"greetings": ["হ্যালো! আমি আপনাকে কীভাবে সাহায্য করতে পারি?"]} }
}

# --- 4. VOICE LOGIC ---
def speak_text(text, lang):
    lang_map = {"English": "en-US", "Hindi": "hi-IN", "Bengali": "bn-IN"}
    l_code = lang_map.get(lang, "en-US")
    clean_text = text.replace('"', "'").replace('\n', ' ')
    components.html(f"""<script>var msg = new SpeechSynthesisUtterance("{clean_text}"); msg.lang = "{l_code}"; window.speechSynthesis.speak(msg);</script>""", height=0)

def voice_input_js(lang):
    lang_map = {"English": "en-US", "Hindi": "hi-IN", "Bengali": "bn-IN"}
    l_code = lang_map.get(lang, "en-US")
    components.html(f"""<script>const r = new (window.SpeechRecognition || window.webkitSpeechRecognition)(); r.lang='{l_code}'; r.onresult=(e)=>{{const t=e.results[0][0].transcript; const d=window.parent.document; const i=d.querySelector('textarea'); if(i){{i.value=t; i.dispatchEvent(new Event('input',{{bubbles:true}}));}}}}; r.start();</script>""", height=0)

# --- 5. SIDEBAR (RESTORED) ---
with st.sidebar:
    st.title("⚙️ Settings")
    lang_choice = st.selectbox("Language / ভাষা / भाषा", ["English", "Hindi", "Bengali"])
    L = LANG_DICT[lang_choice]
    
    st.divider()
    if not st.session_state.logged_in:
        st.subheader("🔐 Account")
        auth_mode = st.radio("Mode", ["Login", "Sign Up"], horizontal=True)
        user_in = st.text_input("Username")
        pass_in = st.text_input("Password", type="password")
        if st.button("Authenticate"):
            if auth_mode == "Login":
                if login_user(user_in, pass_in): st.session_state.logged_in = True; st.session_state.username = user_in; st.rerun()
                else: st.error("Invalid Credentials")
            else:
                if add_user(user_in, pass_in): st.success("Account Created! Login now.")
                else: st.error("User already exists.")
    else:
        st.success(f"Logged in as: {st.session_state.username}")
        if st.button("Logout"): st.session_state.logged_in = False; st.session_state.username = ""; st.rerun()
    
    st.divider()
    st.error(L["emergency"])
    st.markdown(f"**Tele MANAS:** 14416\n\n**Helpline:** 033-24637401")
    if st.button("🗑️ Clear Chat History"): st.session_state.messages = []; st.rerun()

# --- 6. CUSTOM CSS (SMOOTH ANIMATION FIXED) ---
st.markdown(f"""
<style>
    .stApp {{ background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }}
    .stRadio > div {{ flex-direction: row; justify-content: center; background: white; padding: 10px; border-radius: 50px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px; }}
    .chat-bubble {{ padding: 12px 18px; border-radius: 20px; margin-bottom: 15px; max-width: 85%; font-family: sans-serif; line-height: 1.6; border: 1px solid rgba(0,0,0,0.05); }}
    .assistant-bubble {{ background-color: #ffffff; align-self: flex-start; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }}
    .user-bubble {{ background-color: #88c9bf; color: white; margin-left: auto; text-align: left; box-shadow: -2px 2px 10px rgba(0,0,0,0.1); }}
    
    .breath-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 400px; background: white; border-radius: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
    .visualizer {{ width: 250px; height: 250px; border-radius: 50%; border: 8px solid #f0f2f6; display: flex; align-items: center; justify-content: center; position: relative; }}
    
    .inner-circle {{ 
        width: 80px; height: 80px; 
        background: #88c9bf; 
        border-radius: 50%; 
        animation: breatheCycleSmooth 19s infinite ease-in-out; 
    }}
    
    .breath-label {{ font-size: 1.6rem; font-weight: bold; color: #2c3e50; margin-top: 25px; letter-spacing: 1px; }}
    .breath-label::after {{ content: 'Focus...'; animation: labelCycleSmooth 19s infinite; }}

    @keyframes breatheCycleSmooth {{
        0%, 100%, 5% {{ width: 80px; height: 80px; opacity: 0.5; }} 
        21% {{ width: 220px; height: 220px; opacity: 1; }} 
        58% {{ width: 220px; height: 220px; opacity: 1; }}
        100% {{ width: 80px; height: 80px; opacity: 0.5; }}
    }}
    @keyframes labelCycleSmooth {{
        0%, 5% {{ content: 'Ready...'; }}
        6%, 21% {{ content: 'Inhale (4s)'; }}
        22%, 58% {{ content: 'Hold (7s)'; }}
        59%, 99% {{ content: 'Exhale (8s)'; }}
    }}
</style>
""", unsafe_allow_html=True)

# --- 7. MAIN INTERFACE ---
st.markdown(f"<h1 style='text-align: center;'>{L['title']}</h1>", unsafe_allow_html=True)
nav_options = [L["chat_tab"], L["phq_tab"], L["breath_tab"], L["cloud_tab"]]
selected_page = st.radio("", options=nav_options, horizontal=True, label_visibility="collapsed")
st.divider()

# --- TAB 1: HYPER-RESPONSIVE ASSISTANT ---
if selected_page == L["chat_tab"]:
    col1, col2 = st.columns([9, 1])
    with col2: 
        if st.button("🎙️"): voice_input_js(lang_choice)
    
    for i, m in enumerate(st.session_state.messages):
        role_class = "user-bubble" if m["role"] == "user" else "assistant-bubble"
        st.write(f'<div class="chat-bubble {role_class}">{m["content"]}</div>', unsafe_allow_html=True)
        if m["role"] == "assistant" and st.button(f"🔊 Listen", key=f"sp_{i}"): speak_text(m["content"], lang_choice)
            
    if prompt := st.chat_input("Tell me what's on your mind..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # ADVANCED RESPONSIVE BRAIN
        sentiment = TextBlob(prompt).sentiment.polarity
        user_input = prompt.lower()
        
        # Response Logic Engine
        if any(w in user_input for w in ["hi", "hello", "hey", "namaste"]):
            bot_res = random.choice(L["responses"]["greetings"])
        
        elif "sleep" in user_input or "tired" in user_input:
            bot_res = "I hear how exhausted you are. Poor sleep can make everything feel heavy. 🌙 **Solution:** Try setting a 'Digital Sunset'—no screens 45 minutes before bed. You could also try the 4-7-8 breathing method in the next tab."
        
        elif "exam" in user_input or "study" in user_input or "test" in user_input:
            bot_res = "Exam stress is real and very draining. 📚 **Strategy:** Break your study into 25-minute Pomodoro sessions. Focus only on one small chapter today. You're doing your best, and that’s enough."
        
        elif "stress" in user_input or "work" in user_input or "pressure" in user_input:
            bot_res = "That sounds like a heavy load to carry. ⚖️ **Action Plan:** Write down the top 3 tasks stressing you out. Focus only on the first one. Let the rest wait until tomorrow. Take a deep breath with me."
        
        elif "alone" in user_input or "lonely" in user_input or "nobody" in user_input:
            bot_res = "It’s hard to feel like you're on your own. 🤝 **Suggestion:** Sometimes just hearing a human voice helps. Could you call one person today, even if just for 2 minutes? I'm here to chat whenever you need."
        
        elif "anxious" in user_input or "scared" in user_input or "panic" in user_input:
            bot_res = "Let's bring you back to safety right now. ⚓ **Grounding Technique:** Name 5 things you can see and 4 things you can touch. Your heart rate will slow down. You are safe here."
        
        elif "family" in user_input or "parent" in user_input or "friend" in user_input:
            bot_res = "Relationships are complex and can be hurtful. 🫂 **Perspective:** You cannot control others, but you can set boundaries for your own peace. Focus on what you need to feel okay today."
        
        elif sentiment < -0.4:
            bot_res = "I’m truly sorry you're feeling this low. 🌱 **Small Step:** Try to drink a glass of water and look out a window for a moment. Small movements help shift your energy. Would you like to talk more?"
        
        else:
            bot_res = "I'm listening closely. It sounds like you've been through a lot. Can you tell me a bit more about what’s making you feel this way? I'm here to figure it out with you."

        st.session_state.messages.append({"role": "assistant", "content": bot_res})
        if st.session_state.logged_in and "**" in bot_res:
            st.session_state.last_sol = bot_res
        st.rerun()

    if st.session_state.logged_in and "last_sol" in st.session_state:
        st.info("💡 Useful advice detected! Want to track this as a personal goal?")
        if st.button("💾 Yes, Save to my Goals"):
            add_goal(st.session_state.username, st.session_state.last_sol.split("**")[-1])
            del st.session_state.last_sol
            st.success("Goal Saved! Visit the 'Progress & Goals' tab to track it.")

# --- TAB 2: PHQ-9 (PATIENT DETAILS RESTORED) ---
elif selected_page == L["phq_tab"]:
    st.subheader("📊 Clinical PHQ-9 Assessment")
    st.write("### Patient Information")
    c1, c2, c3 = st.columns(3)
    p_name = c1.text_input("Patient Full Name")
    p_age = c2.number_input("Age", 1, 120, 25)
    p_gender = c3.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
    
    st.divider()
    st.write("#### Over the last 2 weeks, how often have you been bothered by:")
    opts = ["Not at all", "Several days", "More than half the days", "Nearly every day"]
    scores = []
    for i, q in enumerate(L["q_list"]):
        scores.append(opts.index(st.radio(f"**{i+1}. {q}**", opts, key=f"q{i}", horizontal=True)))
    
    if st.button("Generate Professional Report", type="primary"):
        if not p_name: st.warning("Please enter patient name.")
        else:
            total = sum(scores)
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "MINDCARE INDIA - CLINICAL REPORT", ln=True, align='C')
            pdf.ln(10); pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, f"Patient Name: {p_name}", ln=True)
            pdf.cell(0, 10, f"Age: {p_age} | Gender: {p_gender}", ln=True)
            pdf.cell(0, 10, f"Total PHQ-9 Score: {total}/27", ln=True)
            pdf.ln(10); pdf.cell(0,10, "Disclaimer: This is a screening tool, not a clinical diagnosis.", ln=True)
            st.success(f"Assessment complete. Total Score: {total}")
            st.download_button("📥 Download PDF Report", pdf.output(dest='S').encode('latin-1'), f"Report_{p_name}.pdf")

# --- TAB 3: BREATHING (SMOOTH & STEADY) ---
elif selected_page == L["breath_tab"]:
    st.subheader("🧘 Clinical 4-7-8 Breathing Space")
    st.info("Follow the circle carefully. This technique resets your nervous system.")
    st.markdown('<div class="breath-container"><div class="visualizer"><div class="inner-circle"></div></div><div class="breath-label"></div></div>', unsafe_allow_html=True)
    

# --- TAB 4: GOALS ---
elif selected_page == L["cloud_tab"]:
    if not st.session_state.logged_in: st.warning("Please login via the sidebar to track your goals.")
    else:
        st.write(f"### 🎯 {st.session_state.username}'s Active Goals")
        goals = get_goals(st.session_state.username)
        if goals:
            for g_id, g_text, g_status in goals:
                col_g1, col_g2 = st.columns([5,1])
                col_g1.info(f"📅 {g_text}")
                if col_g2.button("Done ✅", key=f"g_{g_id}"): delete_goal(g_id); st.rerun()
        else: st.write("No goals set yet. Talk to the assistant to get some suggestions!")
 