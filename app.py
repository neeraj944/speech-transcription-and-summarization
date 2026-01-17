import streamlit as st
import speech_recognition as sr
from transformers import pipeline

#  PAGE CONFIG 
st.set_page_config(
    page_title="Speech Transcription & Summary",
    layout="centered"
)

# CUSTOM CSS 
st.markdown(
    """
    <style>
    body {
        background-color: #0f172a;
        color: #e5e7eb;
    }

    .stApp {
        background-color: #0f172a;
    }

    h1, h2, h3, h4, h5, h6, p, label, span, div {
        color: #e5e7eb !important;
    }

    textarea {
        background-color: #020617 !important;
        color: #e5e7eb !important;
        border: 1px solid #334155 !important;
        border-radius: 8px;
    }

    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
    }

    .stButton>button:hover {
        background-color: #1e40af;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

#  TITLE 
st.title(" SPEECH TRANSCRIPTION & SUMMARIZATION")

st.write(
    """
    **Instructions**
    1. Select your language  
    2. Click **Record Audio** and speak  
    3. Click **Generate Summary**
    """
)

#  LANGUAGE 
language = st.radio("Select speaking language", ["English", "Malayalam"])

#  SESSION STATE 
if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "summary" not in st.session_state:
    st.session_state.summary = ""

# QUESTION MARK LOGIC
def add_question_mark(text):
    question_words = (
        "what", "why", "how", "when", "where", "who",
        "can", "do", "is", "are", "will", "should", "could", "would"
    )
    words = text.strip().split()
    if not words:
        return text
    if words[0].lower() in question_words:
        return text.strip() + "?"
    return text

#  SPEECH RECOGNITION 
recognizer = sr.Recognizer()
recognizer.pause_threshold = 4.5
recognizer.non_speaking_duration = 0.8
microphone = sr.Microphone()

def record_audio():
    with microphone as source:
        st.info(" Listening... Speak clearly")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        if language == "English":
            text = recognizer.recognize_google(audio, language="en-IN")
            text = add_question_mark(text)
        else:
            text = recognizer.recognize_google(audio, language="ml-IN")

    except sr.UnknownValueError:
        text = "[Could not understand audio]"
    except sr.RequestError as e:
        text = f"[API error: {e}]"

    st.session_state.transcript += text + " "

#  SUMMARIZER 
@st.cache_resource
def load_summarizer():
    return pipeline("summarization")

summarizer = load_summarizer()

def generate_summary(text):
    try:
        result = summarizer(
            text,
            max_length=130,
            min_length=30,
            do_sample=False
        )
        return result[0]["summary_text"]
    except Exception as e:
        return f"Summary error: {e}"

#  BUTTONS 
col1, col2 = st.columns(2)

with col1:
    if st.button(" Record Audio"):
        record_audio()

with col2:
    if st.button(" Generate Summary"):
        if st.session_state.transcript.strip():
            st.session_state.summary = generate_summary(
                st.session_state.transcript
            )
        else:
            st.warning("No transcript available")

# TRANSCRIPT 
st.subheader(" Transcript")
st.text_area(
    label="",
    value=st.session_state.transcript,
    height=260
)

#  SUMMARY
st.subheader(" Summary")
st.text_area(
    label="",
    value=st.session_state.summary,
    height=180
)
