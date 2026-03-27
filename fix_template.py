import re

filepath = r'd:\Cattle Farm System\Cattle_Farm\systemapp\templates\systemapp\compare_cattle.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix ALL multiline {% endif %} and {% if %} tags
# Pattern: {% endif followed by whitespace then %}
content = re.sub(r'\{%\s+endif\s+%\}', '{% endif %}', content)

# Pattern: {% if ... split across lines (whitespace before ==)
content = re.sub(
    r"\{%\s+if\s+cattle\.cattle_type\s+==\s+'COW'\s+%\}",
    "{% if cattle.cattle_type == 'COW' %}",
    content
)

# Fix split forloop.counter == N tags
content = re.sub(
    r"\{%\s+if\s+forloop\.counter\s+==\s+(\d+)\s+%\}",
    r"{% if forloop.counter == \1 %}",
    content
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed all template tags!')

# Verify
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'Cattle_Farm.settings'
import django
django.setup()
from django.template.loader import get_template
try:
    t = get_template('systemapp/compare_cattle.html')
    print('Template compiled OK!')
except Exception as e:
    print(f'Still broken: {e}')
