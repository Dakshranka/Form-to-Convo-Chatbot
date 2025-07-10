import streamlit as st
import requests
from backend.parser import extract_fields
from backend.prompt_generator import generate_prompt
from backend.chatbot_agent import validate_input
from gtts import gTTS
import speech_recognition as sr
import os
import json
import tempfile
from dotenv import load_dotenv

load_dotenv()

import sys
sys.dont_write_bytecode = True

st.set_page_config(page_title="Form-to-Conversational ChatBot", layout="wide")
st.title("Form-to-Conversational ChatBot Tool")

if "fields" not in st.session_state:
    st.session_state.fields = []
if "user_inputs" not in st.session_state:
    st.session_state.user_inputs = {}
if "current_field_index" not in st.session_state:
    st.session_state.current_field_index = 0
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "language" not in st.session_state:
    st.session_state.language = "en"

with st.sidebar:
    st.header("Form Input")
    form_url = st.text_input("Enter Form URL (e.g., govt exam form)", "https://example.gov.in/form")
    uploaded_form = st.file_uploader("Upload HTML Form", type=["html"])
    language = st.selectbox(
        "Select Language",
        ["en", "hi", "te", "ta", "bn", "gu", "mr"],
        format_func=lambda x: {
            "en": "English", "hi": "Hindi", "te": "Telugu",
            "ta": "Tamil", "bn": "Bengali", "gu": "Gujarati", "mr": "Marathi",
        }[x],
    )
    st.session_state.language = language
    use_voice = st.checkbox("Use Voice Input (STT) and Output (TTS)")

    if st.button("Process Form"):
        if form_url or uploaded_form:
            try:
                if uploaded_form:
                    html = uploaded_form.read().decode()
                    files = {"form_file": ("form.html", html.encode(), "text/html")}
                else:
                    response = requests.get(form_url)
                    response.raise_for_status()
                    html = response.text
                    files = {"form_file": ("form.html", html.encode(), "text/html")}

                api_response = requests.post("http://localhost:8000/generate-chatbot/", files=files)
                api_response.raise_for_status()
                st.session_state.fields = api_response.json()["fields"]
                st.session_state.user_inputs = {}
                st.session_state.current_field_index = 0
                st.session_state.last_prompt = None
                st.session_state.chat_history = []
                st.success("Form processed successfully!")
            except Exception as e:
                st.error(f"Error processing form: {str(e)}")
        else:
            st.warning("Please provide a form URL or upload an HTML file.")

if st.session_state.fields:
    st.header("Conversational ChatBot")
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "bot":
                st.markdown(f"**Bot ({st.session_state.language}):** {message['content']}")
                if use_voice:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        tts = gTTS(text=message["content"], lang=st.session_state.language)
                        tts.save(fp.name)
                        st.audio(fp.name, format="audio/mp3")
            else:
                st.markdown(f"**You:** {message['content']}")

    if st.session_state.current_field_index < len(st.session_state.fields):
        field = st.session_state.fields[st.session_state.current_field_index]
        prompt = generate_prompt(field, language=st.session_state.language)

        if st.session_state.last_prompt != prompt:
            st.session_state.chat_history.append({"role": "bot", "content": prompt})
            st.session_state.last_prompt = prompt

        if field["type"] == "select":
            user_input = st.selectbox("Select an option:", [""] + field.get("options", []), key=f"input_{st.session_state.current_field_index}")
        elif field["type"] == "input" and field.get("input_type") == "file":
            user_input = st.file_uploader(prompt, type=["jpg", "jpeg", "png", "pdf"], key=f"input_{st.session_state.current_field_index}")
            if user_input:
                st.session_state.user_inputs[field["name"]] = user_input
        else:
            user_input = st.text_input(prompt, key=f"input_{st.session_state.current_field_index}")

        if use_voice and field["type"] != "select" and field.get("input_type") != "file":
            if st.button("Record Voice Input"):
                recognizer = sr.Recognizer()
                try:
                    with sr.Microphone() as source:
                        st.write("Speak now...")
                        audio = recognizer.listen(source, timeout=5)
                        user_input = recognizer.recognize_google(audio, language=st.session_state.language)
                        st.session_state.user_inputs[field["name"]] = user_input
                        st.success("Voice input recorded!")
                except sr.WaitTimeoutError:
                    st.warning("Listening timed out—please try again or use text input.")
                except sr.UnknownValueError:
                    st.warning("Could not understand audio.")
                except sr.RequestError:
                    st.error("Speech recognition service unavailable.")
                except Exception as e:
                    st.error(f"Error with microphone: {str(e)}")

        if st.button("Submit Response"):
            if field["type"] == "select" and not user_input:
                st.warning("Please select an option.")
            elif field["type"] == "input" and field.get("input_type") == "file" and not st.session_state.user_inputs.get(field["name"]):
                st.warning("Please upload a file.")
            elif user_input or (field["type"] == "input" and field.get("input_type") == "file" and st.session_state.user_inputs.get(field["name"])):
                is_valid = True
                error = ""
                if field["type"] in ["input", "textarea"] and field.get("input_type") != "file":
                    is_valid, error = validate_input(field, user_input if not st.session_state.user_inputs.get(field["name"]) else str(st.session_state.user_inputs[field["name"]]))
                if is_valid:
                    if field["type"] in ["input", "textarea"] and field.get("input_type") != "file" and not st.session_state.user_inputs.get(field["name"]):
                        st.session_state.user_inputs[field["name"]] = user_input
                    st.session_state.chat_history.append({"role": "user", "content": user_input if isinstance(user_input, str) else "File uploaded"})
                    st.session_state.current_field_index += 1
                    st.session_state.last_prompt = None
                    st.rerun()
                else:
                    st.error(error)
            else:
                st.warning("Please provide a response.")

    else:
        st.markdown("**All fields collected!**")
        if st.button("Submit Form"):
            with st.spinner("Filling and submitting form..."):
                try:
                    submit_url = form_url if form_url and form_url.startswith("http") else "file://D:/form-to-convo/form.html"
                    if not os.path.exists(os.path.abspath("D:/form-to-convo/form.html")) and not form_url:
                        st.error("Form HTML file not found. Please upload or provide a valid URL.")
                        st.stop()

                    # Serialize inputs (handle files as filenames only)
                    payload = {
                        "url": submit_url,
                        "inputs": json.dumps({k: (v.name if hasattr(v, "name") else v) for k, v in st.session_state.user_inputs.items()})
                    }

                    response = requests.post("http://localhost:8000/submit-form/", data=payload)
                    if response.ok:
                        st.success("Form submitted successfully!")
                        st.write("Server Response:", response.json())
                    else:
                        st.error(f"Error submitting form: {response.text}")

                    st.session_state.fields = []
                    st.session_state.user_inputs = {}
                    st.session_state.current_field_index = 0
                    st.session_state.last_prompt = None
                    st.session_state.chat_history = []
                except Exception as e:
                    st.error(f"Error submitting form: {str(e)}")
