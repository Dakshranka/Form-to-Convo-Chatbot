import google.generativeai as genai
import os
from google.cloud import translate_v2 as translate
import asyncio
from dotenv import load_dotenv
from functools import lru_cache
from google.oauth2 import service_account

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
credentials = service_account.Credentials.from_service_account_file(credentials_path)
translate_client = translate.Client(credentials=credentials)

@lru_cache(maxsize=100)
def generate_base_prompt(label, input_type, required, options):
    gemini_prompt = f"""
    Generate a natural, conversational prompt for:
    - Label: {label}
    - Type: {input_type}
    - Required: {required}
    - Options: {', '.join(options)}
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(gemini_prompt)
        return response.text.strip()
    except:
        return f"What is your {label}?"

async def translate_text(text, dest):
    return translate_client.translate(text, target_language=dest)['translatedText']

def generate_prompt(field, language="en"):
    label = field['label'].replace('_', ' ').capitalize()
    input_type = field.get('input_type', 'text')
    required = field['required']
    options = tuple(field.get('options', []))
    prompt = generate_base_prompt(label, input_type, required, options)

    if language != "en":
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            prompt = loop.run_until_complete(translate_text(prompt, language))
        except Exception as e:
            print(f"Translation error: {e}")
    return prompt