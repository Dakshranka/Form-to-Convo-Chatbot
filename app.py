import streamlit as st
import requests
from backend.parser import extract_fields
from backend.prompt_generator import generate_prompt
from backend.chatbot_agent import validate_input
from backend.form_filler import sync_fill_form
from gtts import gTTS
import speech_recognition as sr
import os
import json
import tempfile
from dotenv import load_dotenv
import uuid
from datetime import datetime
from dateutil import parser

load_dotenv()

# Disable .pyc file generation to avoid watcher issues
import sys
sys.dont_write_bytecode = True

st.set_page_config(page_title="Form-to-Conversational ChatBot", layout="wide")

st.title("Form-to-Conversational ChatBot Tool")

# Initialize session state
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
if "form_url" not in st.session_state:
    st.session_state.form_url = ""
if "uploaded_form" not in st.session_state:
    st.session_state.uploaded_form = None

# Load saved session if exists and not processing new form
if os.path.exists("session_data.json") and not st.session_state.uploaded_form and not st.session_state.form_url:
    try:
        with open("session_data.json", "r") as f:
            session_data = json.load(f)
            st.session_state.update(session_data)
    except json.JSONDecodeError:
        st.warning("Invalid session data, starting fresh.")
        if os.path.exists("session_data.json"):
            os.remove("session_data.json")

# Sidebar for form input and settings
with st.sidebar:
    st.header("Form Input & Settings")
    st.session_state.form_url = st.text_input("Enter Form URL (e.g., https://example.gov.in/form)", value=st.session_state.form_url)
    st.session_state.uploaded_form = st.file_uploader("Upload HTML Form", type=["html"], key="html_uploader")
    language = st.selectbox(
        "Select Language",
        ["en", "hi", "te", "ta", "bn", "gu", "mr"],
        format_func=lambda x: {
            "en": "English", "hi": "Hindi", "te": "Telugu",
            "ta": "Tamil", "bn": "Bengali", "gu": "Gujarati", "mr": "Marathi",
        }[x],
        key="language_select"
    )
    st.session_state.language = language
    use_voice = st.checkbox("Use Voice Input (STT) and Output (TTS)", key="voice_checkbox")

    if st.button("Process Form", key="process_button"):
        if st.session_state.form_url or st.session_state.uploaded_form:
            # Reset session state for new form
            st.session_state.fields = []
            st.session_state.user_inputs = {}
            st.session_state.current_field_index = 0
            st.session_state.last_prompt = None
            st.session_state.chat_history = []
            try:
                if st.session_state.uploaded_form:
                    html = st.session_state.uploaded_form.read().decode()
                    files = {"form_file": ("form.html", html.encode(), "text/html")}
                else:
                    response = requests.get(st.session_state.form_url, timeout=30)
                    response.raise_for_status()
                    html = response.text
                    files = {"form_file": ("form.html", html.encode(), "text/html")}

                api_response = requests.post("http://localhost:8000/generate-chatbot/", files=files, timeout=30)
                api_response.raise_for_status()
                st.session_state.fields = api_response.json()["fields"]
                st.success("Form processed successfully!")
            except Exception as e:
                st.error(f"Error processing form: {str(e)}")
        else:
            st.warning("Please provide a form URL or upload an HTML file.")

# Main chat interface
if st.session_state.fields:
    st.header("Conversational ChatBot")
    chat_container = st.container()

    with chat_container:
        st.subheader("Chat History")
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
        st.subheader("Current Interaction")
        field = st.session_state.fields[st.session_state.current_field_index]
        prompt = generate_prompt(field, language=st.session_state.language)

        if st.session_state.last_prompt != prompt:
            st.session_state.chat_history.append({"role": "bot", "content": prompt})
            st.session_state.last_prompt = prompt

        if field["type"] == "select":
            user_input = st.selectbox("Select an option:", [""] + field.get("options", []), key=f"input_{st.session_state.current_field_index}")
            st.session_state.user_inputs[field["name"]] = user_input
        elif field["type"] == "input" and field.get("input_type") == "file":
            user_input = st.file_uploader(prompt, type=["jpg", "jpeg", "png", "pdf"], key=f"input_{st.session_state.current_field_index}")
            if user_input:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{user_input.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(user_input.read())
                st.session_state.user_inputs[field["name"]] = tmp_file.name
        elif field["type"] == "input" and "date" in field.get("input_type", "").lower():
            user_input = st.text_input(prompt, value=st.session_state.user_inputs.get(field["name"], ""), key=f"input_{st.session_state.current_field_index}")
            st.session_state.user_inputs[field["name"]] = user_input
        else:
            user_input = st.text_input(prompt, value=st.session_state.user_inputs.get(field["name"], ""), key=f"input_{st.session_state.current_field_index}")
            st.session_state.user_inputs[field["name"]] = user_input

        if use_voice and field["type"] != "select" and field.get("input_type") != "file":
            if st.button("Record Voice Input", key=f"voice_{st.session_state.current_field_index}"):
                recognizer = sr.Recognizer()
                try:
                    with sr.Microphone() as source:
                        st.write("Speak now...")
                        audio = recognizer.listen(source, timeout=5)
                        user_input = recognizer.recognize_google(audio, language=st.session_state.language)
                        if "date" in field.get("input_type", "").lower():
                            try:
                                user_input = parser.parse(user_input).strftime("%Y-%m-%d")
                            except ValueError:
                                pass
                        st.session_state.user_inputs[field["name"]] = user_input
                        st.rerun()
                        st.success("Voice input recorded!")
                except sr.WaitTimeoutError:
                    st.warning("Listening timed out—please try again or use text input.")
                except sr.UnknownValueError:
                    st.warning("Could not understand audio.")
                except sr.RequestError:
                    st.error("Speech recognition service unavailable.")
                except Exception as e:
                    st.error(f"Error with microphone: {str(e)}")

        if st.button("Submit Response", key=f"submit_{st.session_state.current_field_index}"):
            value = st.session_state.user_inputs.get(field["name"], "").strip()
            if field["required"] and not value:
                st.warning(f"{field['label']} is required.")
            elif field["type"] == "select" and not value:
                st.warning("Please select an option.")
            elif field["type"] == "input" and field.get("input_type") == "file" and not st.session_state.user_inputs.get(field["name"]):
                st.warning("Please upload a file.")
            else:
                is_valid = True
                error = ""
                if field["type"] in ["input", "textarea"] and field.get("input_type") != "file":
                    is_valid, error = validate_input(field, value)
                if is_valid:
                    st.session_state.chat_history.append({"role": "user", "content": value if isinstance(value, str) else "File uploaded"})
                    st.session_state.current_field_index += 1
                    st.session_state.last_prompt = None
                    st.rerun()
                else:
                    st.warning(error)

    else:
        st.subheader("Form Submission")
        st.markdown("**All fields collected!**")
        if st.button("View Submissions", key="view_submissions"):
            log_path = os.path.join(os.getcwd(), "submission_log.json")
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r") as f:
                        submissions = json.load(f)
                        if submissions:
                            st.json(submissions[-1])  # Show only latest if exists
                        else:
                            st.warning("No submissions found in log.")
                except json.JSONDecodeError:
                    st.warning("Invalid submission log data, resetting.")
                    with open(log_path, "w") as f:
                        json.dump([], f)
            else:
                st.warning("No submissions found.")
        if st.button("Submit Form", key="final_submit"):
            with st.spinner("Filling and submitting form..."):
                try:
                    submit_url = st.session_state.form_url if st.session_state.form_url and st.session_state.form_url.startswith("http") else "file://D:/form-to-convo/form.html"
                    if not os.path.exists(os.path.abspath("D:/form-to-convo/form.html")) and not st.session_state.form_url:
                        st.error("Form HTML file not found. Please upload or provide a valid URL.")
                        st.stop()

                    # Extract only JSON-serializable data
                    session_data = {
                        "user_inputs": {k: v for k, v in st.session_state.user_inputs.items() if not hasattr(v, "name")},
                        "fields": st.session_state.fields,
                        "current_field_index": st.session_state.current_field_index,
                        "last_prompt": st.session_state.last_prompt,
                        "chat_history": st.session_state.chat_history,
                        "language": st.session_state.language,
                        "form_url": st.session_state.form_url,
                        "uploaded_form": None if not st.session_state.uploaded_form else st.session_state.uploaded_form.name
                    }

                    payload = {
                        "url": submit_url,
                        "inputs": json.dumps({k: (v.name if hasattr(v, "name") else v) for k, v in st.session_state.user_inputs.items()})
                    }

                    submit_response = requests.post("http://localhost:8000/submit-form/", data=payload, timeout=30)
                    if not submit_response.ok:
                        st.error(f"Error submitting form: {submit_response.text}")
                        st.stop()

                    # Save session data
                    with open("session_data.json", "w") as f:
                        json.dump(session_data, f)

                    store_response = requests.post("http://localhost:8000/store-submission/", data=payload, timeout=30)
                    if store_response.ok:
                        st.success("Form submitted, data stored, and session saved successfully!")
                        st.write("Server Response:", submit_response.json())
                        log_path = os.path.join(os.getcwd(), "submission_log.json")
                        if os.path.exists(log_path):
                            try:
                                with open(log_path, "r") as f:
                                    submissions = json.load(f)
                                    if submissions:
                                        st.write("Latest Submission Data:", submissions[-1])
                                    else:
                                        st.warning("No submission data available yet.")
                            except json.JSONDecodeError:
                                st.warning("Invalid submission log, resetting.")
                                with open(log_path, "w") as f:
                                    json.dump([], f)
                    else:
                        st.error(f"Error storing submission: {store_response.text}")

                    st.session_state.fields = []
                    st.session_state.user_inputs = {}
                    st.session_state.current_field_index = 0
                    st.session_state.last_prompt = None
                    st.session_state.chat_history = []
                    st.session_state.form_url = ""
                    st.session_state.uploaded_form = None
                except Exception as e:
                    st.error(f"Error submitting form: {str(e)}")