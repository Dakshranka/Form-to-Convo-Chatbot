from backend.prompt_generator import generate_prompt

def chatbot_conversation(fields, language="en"):
    inputs = {}
    for field in fields:
        prompt = generate_prompt(field, language)
        response = input(f"{prompt}\n> ")
        is_valid, error = validate_input(field, response)
        if is_valid:
            inputs[field['name']] = response
        else:
            print(f"Invalid input: {error}")
            return None
    return inputs

def validate_input(field, value):
    if field["required"] and not value.strip():
        return False, f"{field['label']} is required."

    if field["type"] == "input" and field.get("input_type") == "number":
        try:
            float(value)
            label = field["label"].lower()
            name = field["name"].lower()
            if "phone" in label or "phone number" in label or "contact number" in name:
                if not (len(value.strip()) == 10 and value.isdigit()):
                    return False, "Please enter a valid 10-digit phone number."
            elif "aadhaar" in label.lower() or "aadhaar number" in label.lower():
                if not (len(value.strip()) == 12 and value.isdigit()):
                    return False, "Please enter a valid 12-digit Aadhaar number."
                value = f"XXXX-XXXX-{value[-4:]}"
        except ValueError:
            return False, "Please enter a valid number."

    if field["type"] == "input" and field.get("input_type") == "date":
        try:
            from dateutil import parser
            value = parser.parse(value).strftime("%Y-%m-%d")
        except ValueError:
            return False, "Date must be in a valid format (e.g., 14 Nov 2004 or YYYY-MM-DD)."

    if "email" in field["label"].lower() and field.get("input_type") == "email":
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            return False, "Invalid email format."

    return True, ""