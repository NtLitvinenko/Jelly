import re

def parse_nip_markup(markup):
    parsed_data = {
        'styles': {},
        'labels': {},
        'buttons': {},
        'functions': {}
    }

    current_function = None
    lines = markup.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # Match styles
        style_match = re.match(r'^(style_[^:]+):\{(.*)\}$', line)
        if style_match:
            style_name = style_match.group(1)
            attributes_dict = {
                kv.split('=')[0].strip(): kv.split('=')[1].strip()
                for kv in style_match.group(2).split(';') if '=' in kv
            }
            parsed_data['styles'][style_name] = attributes_dict
            continue

        # Match functions
        function_match = re.match(r'^(function_[^:]+)\{', line)
        if function_match:
            current_function = function_match.group(1)
            parsed_data['functions'][current_function] = {'commands': []}
            continue
        elif current_function and line == '}':
            current_function = None
            continue
        elif current_function:
            parsed_data['functions'][current_function]['commands'].append(line.strip())

        # Match labels
        label_match = re.match(r'^(label_[^:]+):(.+)$', line)
        if label_match:
            label_name = label_match.group(1)
            style_reference = label_match.group(2).strip()
            parsed_data['labels'][label_name] = {'style': style_reference}
            continue

        # Match onclick events
        onclick_match = re.match(r'^(button_[^:]+)\.onclick:(.*)$', line)
        if onclick_match:
            element_name = onclick_match.group(1).strip()
            onclick_value = onclick_match.group(2).strip()
            if element_name in parsed_data['buttons']:
                parsed_data['buttons'][element_name]['onclick'] = onclick_value
            continue

        # Match buttons
        button_match = re.match(r'^(button_[^:]+):(.+)$', line)
        if button_match:
            button_name = button_match.group(1)
            style_reference = button_match.group(2).strip()
            parsed_data['buttons'][button_name] = {
                'style': style_reference,
                'onclick': None  # Initialize onclick as None
            }
            continue

    return parsed_data