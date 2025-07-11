
# Form-to-Convo ChatBot

## Team Penguin

- Akshat Arora
- Daksh Ranka
- Sneh Kumar Bhagat

## Problem Statement

Design and build a Form-to-Convo Tool that converts any HTML form, including complex, multi-page, wizard-style forms, into an intelligent, multilingual, conversational chatbot. The chatbot should interpret the form structure, interact with users, validate inputs, and auto-submit the form based on confirmed responses. Key requirements include:

- Support for multi-page "wizard" style forms.
- Conversation preview interface (text or basic web UI).
- Interface in a preferred user language while retaining form data in its original language (using open-source multilingual models like Google Translate).
- A simple streamlit UI for form ingestion (via HTTP URL or HTML upload) and a chat interface for input collection and form filling.
- API-based interaction support.

## Solution Overview

A conversational chatbot that:

- Reads and understands the form structure from HTML.
- Asks natural language questions (e.g., "What is your full name?" or "What is your caste category?").
- Detects and handles invalid/irrelevant responses (e.g., income as "ABC").
- Translates prompts and responses across Indian languages (e.g., Hindi → Telugu).

### Example Input Form (HTML Content)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Student Registration Form</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f2f2f2; padding: 30px; }
    .container { max-width: 600px; margin: auto; background: #fff; padding: 20px 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    h2 { text-align: center; margin-bottom: 25px; color: #333; }
    label { display: block; margin-bottom: 5px; font-weight: bold; }
    input, select, textarea { width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 5px; }
    button { background: #4CAF50; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; }
    button:hover { background: #45a049; }
  </style>
</head>
<body>
  <div class="container">
    <h2>Student Registration Form</h2>
    <form action="/submit" method="POST">
      <label for="fname">First Name *</label>
      <input type="text" id="fname" name="first_name" placeholder="Enter your first name" required>
      <label for="lname">Last Name *</label>
      <input type="text" id="lname" name="last_name" placeholder="Enter your last name" required>
      <label for="dob">Date of Birth *</label>
      <input type="date" id="dob" name="dob" required>
      <label for="gender">Gender *</label>
      <select id="gender" name="gender" required>
        <option value="">-- Select --</option>
        <option value="Male">Male</option>
        <option value="Female">Female</option>
        <option value="Other">Other</option>
      </select>
      <label for="email">Email *</label>
      <input type="email" id="email" name="email" placeholder="example@domain.com" required>
      <label for="phone">Phone Number *</label>
      <input type="tel" id="phone" name="phone" placeholder="10-digit number" pattern="[0-9]{10}" required>
      <label for="address">Address</label>
      <textarea id="address" name="address" rows="3" placeholder="Your address..."></textarea>
      <label for="state">State *</label>
      <input type="text" id="state" name="state" required>
      <label for="city">City *</label>
      <input type="text" id="city" name="city" required>
      <label for="pincode">Pincode *</label>
      <input type="text" id="pincode" name="pincode" pattern="[0-9]{6}" placeholder="6-digit pincode" required>
      <label for="course">Course Applied For *</label>
      <select id="course" name="course" required>
        <option value="">-- Select Course --</option>
        <option value="B.Tech">B.Tech</option>
        <option value="B.Sc">B.Sc</option>
        <option value="B.Com">B.Com</option>
        <option value="BA">BA</option>
        <option value="MBA">MBA</option>
        <option value="M.Tech">M.Tech</option>
      </select>
      <label for="photo">Upload Photo *</label>
      <input type="file" id="photo" name="photo" accept="image/*" required>
      <label for="doc">Upload ID Proof *</label>
      <input type="file" id="doc" name="id_proof" accept=".pdf,.jpg,.png" required>
      <button type="submit">Submit Registration</button>
    </form>
  </div>
</body>
</html>
```

## Implementation Guidance

### Architecture Sketch
- HTML Form Parsing → Prompt Generator → Conversational Agent (LangChain)
- Input Validator → Multilingual Translator → Form Auto-filler (headless browser/API) → Submit

### Phases

1. **HTML Form Parsing**: Using BeautifulSoup or Playwright to parse and navigate the DOM, extracting fields, labels, input types, and validation constraints.
2. **Prompt Generation**: Generating natural language questions using field metadata, potentially with LLM Gemini API.
3. **Conversational Agent**: Implementing with LangChain agents or gTTS (Google Text-to-Speech Python library) for conversation orchestration and basic fallback logic.
4. **Translation**: Integrating Google Translator API for multi-language support across Indian languages.
5. **Form Auto-filler & Submit**: Using Playwright to auto-populate fields and simulate submission.
6. **API Support**: Exposing APIs like '/generate-chatbot/' and '/submit-form/' using FastAPI.

## Tech Stack Used

| Functionality          | Tech Stack Used                                |
|------------------------|------------------------------------------------|
| HTML Parsing           | BeautifulSoup                                  |
| LLM + Agents           | Python, LangChain, Gemini API                 |
| Translation            | Google Translate                               |
| Conversational Interface | Streamlit                                     |
| Form Autofill          | Playwright                                     |
| API Support            | FastAPI                                        |
| Deployment             | GitHub                                         |

## API Support

- **/generate-chatbot**: Generates the chatbot for the provided form.
- **/submit-form**: Submits the filled-out form to the backend after user confirmation.

## Workflow Diagram

![Workflow Diagram](![WhatsApp Image 2025-07-11 at 21 10 52_bf4e1c9b](https://github.com/user-attachments/assets/21ca668d-da92-4cba-860d-3f2aa70529b2)


## Procedure to Run the Project

Follow these steps to run the Form-to-Convo ChatBot project on your local machine:

### Prerequisites

Make sure you have the following installed:

- Python (version 3.7 or higher)
- Pip (Python package manager)
- Git (optional for cloning the repo)

### Step 1: Clone the Repository

Clone the repository using the following command:

```bash
git clone https://github.com/YourUsername/Form-to-Convo-Chatbot.git
```

Navigate into the project directory:

```bash
cd Form-to-Convo-Chatbot
```

### Step 2: Set Up a Virtual Environment

It is recommended to use a virtual environment to manage dependencies:

```bash
python3 -m venv env
source env/bin/activate  # For Windows, use `env\Scriptsctivate`
```

### Step 3: Install Required Packages

Install all required Python packages from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

Start the application using the following command:

```bash
python app.py
```

or

```bash
streamlit run app.py  # If using Streamlit for the UI
```

This will start a local server. You can access the app in your browser at `http://localhost:8501`.

### Step 5: Accessing the Form

Once the application is running, you can access the form through the provided UI (Streamlit). Upload the HTML form or provide a URL to an existing form. The chatbot will guide you through filling the form interactively.

### Step 6: Testing the API

To interact with the backend APIs, you can use the following endpoints:

- **POST /generate-chatbot**: Generates the chatbot for the form.
- **POST /submit-form**: Submits the completed form after confirmation.

### Step 7: Deployment

For deployment, you can push the code to a cloud platform (e.g., Heroku, AWS, GCP). Ensure that all environment variables and dependencies are properly configured.

## Conclusion

The Form-to-Convo ChatBot project successfully delivers a robust, multilingual, and interactive solution for converting HTML forms into a conversational interface, aligning with the hackathon's objectives. By leveraging technologies such as Streamlit for a responsive user interface, FastAPI for API support, Playwright for form autofill, and Google Translate for multilingual translation, the tool effectively handles complex, multi-page forms while supporting voice input/output via gTTS and Google Speech R...

Key achievements include the ability to process diverse form structures, provide a user-friendly interface with enhanced responsiveness, and support multiple Indian languages, ensuring accessibility across linguistic boundaries. The integration of session management and submission logging further enhances usability and data persistence. However, challenges such as handling edge cases in form parsing and optimizing real-time translation performance were encountered, offering opportunities for refinement.

This project lays a strong foundation for transforming traditional form-filling experiences into intelligent, user-centric interactions.
