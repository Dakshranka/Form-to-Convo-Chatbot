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
        return False, "This field is required."

    if field["type"] == "input" and field.get("input_type") == "number":
        try:
            float(value)
            label = field["label"].lower()
            name = field["name"].lower()
            if "phone" in label or "mobile number" in label or "contact number" in label or "phone number" in name:
                if not (len(value.strip()) == 10 and value.isdigit()):
                    return False, "Please enter a valid 10-digit phone number."
        except ValueError:
            return False, "Please enter a valid number."

    if field["type"] == "input" and field.get("input_type") == "date":
        import re
        if not re.match(r"\d{4}-\d{2}-\d{2}", value):
            return False, "Date must be in YYYY-MM-DD format."

    if "email" in field["label"].lower() and field.get("input_type") == "email":
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            return False, "Invalid email format."

    return True, ""
