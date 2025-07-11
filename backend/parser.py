from bs4 import BeautifulSoup
import re

def extract_fields(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        fields = []

        # Target form elements (including dynamic ones)
        for tag in soup.find_all(['input', 'select', 'textarea'], attrs={'name': True}) + \
                   soup.find_all(['input', 'select', 'textarea'], attrs={'id': True, 'role': re.compile(r'input|combobox|textbox', re.I)}):
            # Extract label from various sources
            label_elem = soup.find('label', {'for': tag.get('id')}) or tag.find_previous('label') or \
                         tag.find_parent(['div', 'span', 'p'], class_=re.compile(r'form-label|label|form-input', re.I))
            label_text = (label_elem.get_text(strip=True) if label_elem else tag.get('placeholder') or tag.get('name') or tag.get('id') or "Unnamed Field").replace('*', '').strip()
            
            # Filter out irrelevant fields (e.g., hidden or non-form inputs)
            if not tag.get('type') == 'hidden' and label_text.lower() not in ['submit', 'button']:
                required = tag.has_attr('required') or ("*" in label_text) or (tag.get('aria-required') == 'true')
                field = {
                    'label': label_text,
                    'type': tag.name or 'input',
                    'name': tag.get('name') or tag.get('id') or f"field_{len(fields)}",
                    'required': required,
                    'input_type': tag.get('type') if tag.name == 'input' else (tag.get('role') if tag.get('role') else None),
                    'options': [o.get_text(strip=True) for o in tag.find_all('option')] if tag.name == 'select' else []
                }
                fields.append(field)
        return fields
    except Exception as e:
        print(f"Parsing error: {str(e)}")
        return []