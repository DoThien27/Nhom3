import re
import os

with open('web/static/js/renderers.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find all buttons that have edit or deleteItem in onclick
pattern = r'(<button\s+onclick=[\'\"].*?(?:edit|deleteItem).*?class=[\'\"])(.*?)([\'\"])'
new_content = re.sub(pattern, r'\1\2 admin-only\3', content)

with open('web/static/js/renderers.js', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated renderers.js successfully!")
