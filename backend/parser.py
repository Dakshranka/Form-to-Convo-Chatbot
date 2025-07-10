from bs4 import BeautifulSoup

def extract_fields(html):
    soup = BeautifulSoup(html, 'html.parser')
    forms = soup.find_all('form')
    fields = []

    for form in forms:
        for tag in form.find_all(['input', 'select', 'textarea']):
            field = {
                'label': (form.find('label', {'for': tag.get('id')}) or {}).get_text(strip=True) or tag.get('name'),
                'type': tag.name,
                'name': tag.get('name'),
                'required': tag.has_attr('required'),
                'input_type': tag.get('type') if tag.name == 'input' else None,
                'options': [o.get('value') for o in tag.find_all('option')] if tag.name == 'select' else []
            }
            fields.append(field)
    return fields
