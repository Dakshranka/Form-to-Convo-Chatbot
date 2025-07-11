from datetime import datetime
import uuid
from fastapi import FastAPI, UploadFile, Form
from backend.parser import extract_fields
from backend.form_filler import sync_fill_form
import json
from fastapi import HTTPException
import requests
import os
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/generate-chatbot/")
async def generate_chatbot(form_file: UploadFile = None, url: str = Form(None)):
    if url:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        html = response.text
    elif form_file:
        html = await form_file.read()
    else:
        raise HTTPException(status_code=400, detail="Provide URL or file")
    fields = extract_fields(html.decode())
    return {"fields": fields}

@app.post("/submit-form/")
async def submit_form(url: str = Form(...), inputs: str = Form(...)):
    try:
        field_data = json.loads(inputs)
        logger.info(f"Submitting form to {url} with data: {field_data}")
        await sync_fill_form(url, field_data)
        logger.info("Form submission completed successfully")
        return {"status": "Form submitted successfully"}
    except Exception as e:
        logger.error(f"Error submitting form: {str(e)}")
        return {"error": str(e)}

@app.post("/store-submission/")
async def store_submission(url: str = Form(...), inputs: str = Form(...)):
    try:
        field_data = json.loads(inputs)
        log_path = os.path.join(os.getcwd(), "submission_log.json")
        if not os.path.exists(log_path):
            with open(log_path, "w") as f:
                json.dump([], f)
        with open(log_path, "r+") as f:
            data = json.load(f)
            entry = {
                "id": str(uuid.uuid4()),
                "url": url,
                "data": field_data,
                "timestamp": datetime.now().isoformat()
            }
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
        logger.info(f"Submission stored at {log_path}")
        return {"status": "Submission stored successfully"}
    except Exception as e:
        logger.error(f"Error storing submission: {str(e)}")
        return {"error": str(e)}

@app.post("/save-session/")
async def save_session(inputs: str = Form(...)):
    try:
        session_data = json.loads(inputs)
        with open("session_data.json", "w") as f:
            json.dump(session_data, f, indent=2)
        return {"status": "Session saved successfully"}
    except Exception as e:
        return {"error": str(e)}