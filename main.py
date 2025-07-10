from fastapi import FastAPI, UploadFile, Form
from backend.parser import extract_fields
from backend.form_filler import sync_fill_form
import json
from fastapi import HTTPException

app = FastAPI()

@app.post("/generate-chatbot/")
async def generate_chatbot(form_file: UploadFile = None, url: str = Form(None)):
    if url:
        import requests
        response = requests.get(url)
        response.raise_for_status()
        html = response.text
    elif form_file:
        html = await form_file.read()
    else:
        raise HTTPException(status_code=400, detail="Provide URL or file")
    fields = extract_fields(html.decode())
    return {"fields": fields}

@app.post("/submit-form/")
def submit_form(url: str = Form(...), inputs: str = Form(...)):
    try:
        field_data = json.loads(inputs)
        sync_fill_form(url, field_data)
        return {"status": "Form submitted successfully"}
    except Exception as e:
        return {"error": str(e)}
