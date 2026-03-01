import streamlit as st
from textblob import TextBlob
import pandas as pd
import random
from fpdf import FPDF
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
from datetime import datetime
from collections import Counter
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="MindCare India", page_icon="🧠", layout="wide")

# --- MULTI-LANGUAGE DICTIONARY ---
LANG_DICT = {
    "English": {
        "title": "MindCare India 🧠",
        "chat_tab": "💬 Assistant",
        "phq_tab": "📊 PHQ-9 Check",
        "breath_tab": "🧘 Breathing Space",
        "cloud_tab": "📊 Mood Analytics",
        "emergency": "Emergency Support Lines:",
        "kolkata_help": "Kolkata Helpline: 033-24637401",
        "submit_btn": "Submit Assessment",
        "inhale": "Inhale", "hold": "Hold", "exhale": "Exhale",
        "rhythm": "Follow the circle's rhythm",
        "chat_placeholder": "Say hello or tell me how you feel...",
        "details_header": "Patient Details",
        "name_label": "Full Name",
        "age_label": "Age",
        "gender_label": "Gender",
        "gender_options": ["Male", "Female", "Other", "Prefer not to say"],
        "q_list": [
            "Little interest in things", "Feeling down/hopeless", "Sleep issues", 
            "Low energy", "Appetite issues", "Feeling like a failure", 
            "Concentration trouble", "Slow/restless", "Thoughts of self-harm"
        ],
        "responses": {
            "greetings": ["Hello! How can I help you today?", "Namaste! How are you feeling?", "Hi! I'm here to listen."],
            "wellbeing": ["I'm doing well, thank you for asking! How are you?", "I'm here and ready to support you."],
            "identity": ["I am MindCare, your AI companion.", "I'm an AI designed to help you process your thoughts."],
            "sleep": ["Sleep is vital. Are you struggling to drift off?", "Try a warm drink or reading a physical book before bed."],
            "general": ["Tell me more about that.", "I'm listening.", "That sounds like a lot to carry.", "How does that make you feel?"]
        }
    },
    "Hindi": {
        "title": "माइंडकेयर इंडिया 🧠",
        "chat_tab": "💬 सहायक",
        "phq_tab": "📊 मानसिक जांच",
        "breath_tab": "🧘 सांस का अभ्यास",
        "cloud_tab": "📊 मूड विश्लेषण",
        "emergency": "आपातकालीन सहायता:",
        "kolkata_help": "कोलकाता हेल्पलाइन: 033-24637401",
        "submit_btn": "जमा करें",
        "details_header": "व्यक्तिगत विवरण",
        "name_label": "पूरा नाम",
        "age_label": "आयु",
        "gender_label": "लिंग",
        "gender_options": ["पुरुष", "महिला", "अन्य", "बताना नहीं चाहते"],
        "inhale": "सांस लें", "hold": "रोकें", "exhale": "छोड़ें",
        "rhythm": "चक्र की लय का पालन करें",
        "chat_placeholder": "नमस्ते कहें या अपनी भावनाएं बताएं...",
        "q_list": [
            "कामों में कम दिलचस्पी", "उदास या निराश महसूस करना", "सोने में परेशानी",
            "थकान या ऊर्जा की कमी", "भूख कम या ज्यादा लगना", "खुद को असफल मानना",
            "ध्यान केंद्रित करने में कठिनाई", "सुस्ती या बेचैनी", "खुद को नुकसान पहुँचाने के विचार"
        ],
        "responses": {
            "greetings": ["नमस्ते! मैं आज आपकी कैसे मदद कर सकता हूँ?", "नमस्ते! आप कैसा महसूस कर रहे हैं?", "नमस्ते! मैं आपको सुनने के लिए यहाँ हूँ।"],
            "wellbeing": ["मैं ठीक हूँ, पूछने के लिए धन्यवाद! आप कैसे हैं?", "मैं आपकी मदद के लिए तैयार हूँ।"],
            "identity": ["मैं माइंडकेयर हूँ, आपका एआई साथी।", "मैं एक एआई हूँ जो आपके मानसिक स्वास्थ्य के लिए बना है।"],
            "sleep": ["नींद बहुत जरूरी है। क्या आपको सोने में दिक्कत हो रही है?", "सोने से पहले रिलैক্স करने की कोशिश करें।"],
            "general": ["मुझे इसके बारे में और बताएं।", "मैं सुन रहा हूँ।", "यह चुनौतीपूर्ण लग रहा है।", "आपको कैसा महसूस हो रहा है?"]
        }
    },
    "Bengali": {
        "title": "মাইন্ডকেয়ার ইন্ডিয়া 🧠",
        "chat_tab": "💬 সহায়ক",
        "phq_tab": "📊 মানসিক পরীক্ষা",
        "breath_tab": "🧘 নিশ্বাসের ব্যায়াম",
        "cloud_tab": "📊 মুড বিশ্লেষণ",
        "emergency": "জরুরী সহায়তা লাইন:",
        "kolkata_help": "কলকাতা হেল্পলাইন: ০৩৩-২৪৬৩৭৪০১",
        "submit_btn": "জমা দিন",
        "details_header": "ব্যক্তিগত তথ্য",
        "name_label": "পুরো নাম",
        "age_label": "বয়স",
        "gender_label": "লিঙ্গ",
        "gender_options": ["পুরুষ", "মহিলা", "অন্যান্য", "বলতে ইচ্ছুক নই"],
        "inhale": "নিশ্বাস নিন", "hold": "ধরে রাখুন", "exhale": "নিশ্বাস ছাড়ুন",
        "rhythm": "চক্রের ছন্দ অনুসরণ করুন",
        "chat_placeholder": "হ্যালো বলুন বা আপনার মনের কথা জানান...",
        "q_list": [
            "কাজে আগ্রহ কম পাওয়া", "মন খারাপ বা হতাশ বোধ করা", "ঘুমে সমস্যা",
            "ক্লান্তি বা শক্তির অভাব", "খিদে কমে যাওয়া বা বেশি খাওয়া", "নিজেকে ব্যর্থ মনে হওয়া",
            "মনোযোগ দিতে অসুবিধা", "ধীরে চলাফেরা বা ছটফটানি", "নিজের ক্ষতি করার চিন্তা"
        ],
        "responses": {
            "greetings": ["হ্যালো! আমি আপনাকে কীভাবে সাহায্য করতে পারি?", "নমস্কার! আপনি কেমন বোধ করছেন?", "হ্যালো! আমি আপনার কথা শোনার জন্য আছি।"],
            "wellbeing": ["আমি ভালো আছি, জিজ্ঞাসা করার জন্য ধন্যবাদ! আপনি কেমন আছেন?", "আমি আপনার সহায়তায় প্রস্তুত।"],
            "identity": ["আমি মাইন্ডকেয়ার, আপনার এআই সঙ্গী।", "আমি আপনার মানসিক স্বাস্থ্যের সহায়তার জন্য তৈরি একটি এআই।"],
            "sleep": ["ঘুম খুব দরকারি। আপনার কি ঘুমাতে অসুবিধা হচ্ছে?", "শোয়ার আগে ফোন থেকে দূরে থাকার চেষ্টা করুন।"],
            "general": ["এই বিষয়ে আরো বলুন।", "আমি শুনছি আপনার কথা।", "আপনার মনের কথা শুনে আমি বুঝতে পারছি।", "এটি আপনাকে কেমন অনুভব করাচ্ছে?"]
        }
    }
}

# --- VOICE LOGIC ---
def speak_text(text, lang):
    lang_map = {"English": "en-US", "Hindi": "hi-IN", "Bengali": "bn-IN"}
    l_code = lang_map.get(lang, "en-US")
    components.html(f"""<script>var msg = new SpeechSynthesisUtterance("{text}"); msg.lang = "{l_code}"; window.speechSynthesis.speak(msg);</script>""", height=0)

def voice_input_js(lang):
    lang_map = {"English": "en-US", "Hindi": "hi-IN", "Bengali": "bn-IN"}
    l_code = lang_map.get(lang, "en-US")
    components.html(f"""
        <script>
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = '{l_code}';
        recognition.onresult = (event) => {{
            const text = event.results[0][0].transcript;
            const streamlitDoc = window.parent.document;
            const inputField = streamlitDoc.querySelector('textarea');
            if(inputField) {{
                inputField.value = text;
                inputField.dispatchEvent(new Event('input', {{bubbles:true}}));
            }}
        }};
        recognition.start();
        </script>
    """, height=0)

# --- SESSION STATE ---
if "messages" not in st.session_state: st.session_state.messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    lang_choice = st.selectbox("Language / ভাষা", ["English", "Hindi", "Bengali"])
    L = LANG_DICT[lang_choice]
    st.error(L["emergency"])
    st.markdown(f"- **Tele MANAS:** 14416\n- **{L['kolkata_help']}**")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- CUSTOM CSS ---
st.markdown(f"""<style>
.stApp {{ background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }}
.chat-bubble {{ padding: 12px 18px; border-radius: 20px; margin-bottom: 10px; max-width: 85%; font-family: sans-serif; }}
.assistant-bubble {{ background-color: white; align-self: flex-start; border: 1px solid #ddd; }}
.user-bubble {{ background-color: #88c9bf; color: white; margin-left: auto; }}
.instruction-box {{ background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 5px solid #88c9bf; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }}
.circle-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 350px; }}
.circle {{ width: 100px; height: 100px; background: rgba(136, 201, 191, 0.6); border-radius: 50%; animation: breathCircle 16s infinite linear; display: flex; align-items: center; justify-content: center; position: relative; }}
.breath-text {{ font-weight: bold; color: #2c3e50; font-size: 1.2rem; }}
.breath-text::after {{ content: '{L["inhale"]}'; animation: breathText 16s infinite linear; }}
@keyframes breathCircle {{ 0% {{ transform: scale(1); opacity: 0.4; }} 25% {{ transform: scale(2.5); opacity: 0.9; }} 50% {{ transform: scale(2.5); opacity: 0.9; }} 75% {{ transform: scale(1); opacity: 0.4; }} 100% {{ transform: scale(1); opacity: 0.4; }} }}
@keyframes breathText {{ 0%, 24% {{ content: '{L["inhale"]}'; }} 25%, 49% {{ content: '{L["hold"]}'; }} 50%, 74% {{ content: '{L["exhale"]}'; }} 75%, 100% {{ content: '{L["hold"]}'; }} }}
</style>""", unsafe_allow_html=True)

# --- HEADER & TABS ---
st.title(L["title"])
tab1, tab2, tab3, tab4 = st.tabs([L["chat_tab"], L["phq_tab"], L["breath_tab"], L["cloud_tab"]])

# --- TAB 1: CHAT ---
with tab1:
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("🎙️"): voice_input_js(lang_choice)
    for i, msg in enumerate(st.session_state.messages):
        role_class = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.write(f'<div class="chat-bubble {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)
        if msg["role"] == "assistant" and st.button(f"🔊 Listen", key=f"sp_{i}"):
            speak_text(msg["content"], lang_choice)
    if prompt := st.chat_input(L["chat_placeholder"]):
        st.session_state.messages.append({"role": "user", "content": prompt})
        user_input = prompt.lower()
        res_list = L["responses"]
        if any(word in user_input for word in ["hi", "hello", "hey"]): bot_res = random.choice(res_list["greetings"])
        elif any(word in user_input for word in ["sleep"]): bot_res = random.choice(res_list["sleep"])
        else: bot_res = random.choice(res_list["general"])
        st.session_state.messages.append({"role": "assistant", "content": bot_res})
        st.rerun()

# --- TAB 2: ASSESSMENT ---
with tab2:
    st.subheader(L["phq_tab"])
    st.write(f"### {L['details_header']}")
    c1, c2, c3 = st.columns(3)
    user_name = c1.text_input(L["name_label"])
    user_age = c2.number_input(L["age_label"], 1, 120, 25)
    user_gender = c3.selectbox(L["gender_label"], L["gender_options"])
    st.divider()
    opts = ["Not at all", "Several days", "More than half the days", "Nearly every day"]
    scores = []
    for i, q in enumerate(L["q_list"]):
        choice = st.radio(f"**{i+1}. {q}**", opts, key=f"q{i}", horizontal=True)
        scores.append(opts.index(choice))
    if st.button(L["submit_btn"]):
        if not user_name: st.warning("Please enter your name.")
        else:
            total = sum(scores)
            status = "Severe" if total > 19 else "Moderate" if total > 9 else "Minimal"
            pdf = FPDF()
            pdf.add_page()
            pdf.set_fill_color(44, 62, 80); pdf.rect(0, 0, 210, 45, 'F')
            pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 24)
            pdf.cell(0, 20, "MINDCARE INDIA", ln=True, align='C')
            pdf.ln(30); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12)
            pdf.cell(95, 10, f" Name: {user_name.upper()}", border=1)
            pdf.cell(95, 10, f" Score: {total} / 27", ln=True, border=1)
            pdf.set_y(-30); pdf.set_font("Arial", 'I', 8); pdf.set_text_color(150, 150, 150)
            pdf.multi_cell(0, 5, "Disclaimer: AI screening report. Consult a professional doctor.", align='C')
            report_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button("📥 Download Official Report", report_bytes, f"MindCare_{user_name}.pdf")

# --- TAB 3: BREATHING ---
with tab3:
    st.subheader(L["breath_tab"])
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        st.markdown(f"""<div class="instruction-box">1. 🌬️ <b>{L['inhale']}</b>: Circle grows (4s).<br><br>2. 🛑 <b>{L['hold']}</b>: Keep it full (4s).<br><br>3. 🌬️ <b>{L['exhale']}</b>: Circle shrinks (4s).<br><br>4. 🛑 <b>{L['hold']}</b>: Keep it small (4s).</div>""", unsafe_allow_html=True)
    with col_b2:
        st.markdown("""<audio autoplay loop><source src="https://www.soundjay.com/nature/sounds/ocean-wave-1.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)
        st.markdown('<div class="circle-container"><div class="circle"><span class="breath-text"></span></div></div>', unsafe_allow_html=True)

# --- TAB 4: UPGRADED MOOD ANALYTICS ---
with tab4:
    user_text = " ".join([m["content"] for m in st.session_state.messages if m["role"]=="user"]).lower()
    
    if user_text:
        st.subheader("Your Emotional Insights")
        
        # Sentiment Analysis
        analysis = TextBlob(user_text)
        sentiment_score = analysis.sentiment.polarity
        
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            # Pie Chart for Sentiment
            pos = len([w for w in user_text.split() if TextBlob(w).sentiment.polarity > 0])
            neg = len([w for w in user_text.split() if TextBlob(w).sentiment.polarity < 0])
            neu = len(user_text.split()) - (pos + neg)
            
            fig1, ax1 = plt.subplots(figsize=(5, 5))
            ax1.pie([pos, neg, neu], labels=['Positive', 'Negative', 'Neutral'], 
                    autopct='%1.1f%%', colors=['#88c9bf', '#ff9999', '#e0e0e0'], startangle=90)
            ax1.set_title("Sentiment Distribution")
            st.pyplot(fig1)

        with col_m2:
            # Bar Chart for Keywords
            words = re.findall(r'\w+', user_text)
            # Filter common filler words
            stop_words = ["i", "me", "my", "am", "is", "are", "the", "a", "an", "and", "to", "feel", "feeling"]
            filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
            word_counts = Counter(filtered_words).most_common(5)
            
            if word_counts:
                df_words = pd.DataFrame(word_counts, columns=['Word', 'Count'])
                fig2, ax2 = plt.subplots(figsize=(5, 5))
                ax2.bar(df_words['Word'], df_words['Count'], color='#88c9bf')
                ax2.set_title("Top Emotional Keywords")
                st.pyplot(fig2)

        st.divider()
        st.write("### Mood Word Cloud")
        wc = WordCloud(width=800, height=300, background_color="white", colormap="viridis").generate(user_text)
        fig3, ax3 = plt.subplots()
        ax3.imshow(wc)
        ax3.axis("off")
        st.pyplot(fig3)
    else:
        st.info("Start chatting with the assistant to see your mood analysis here!")