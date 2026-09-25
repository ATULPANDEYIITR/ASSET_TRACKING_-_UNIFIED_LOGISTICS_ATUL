from pathlib import Path

path = Path("backend/app/main.py")
text = path.read_text(encoding="utf-8-sig")

import_line = "from backend.app.api import events as events_api"

if import_line not in text:
    text = import_line + "\n" + text

router_line = "app.include_router(events_api.router)"

if router_line not in text:
    text = text.rstrip() + "\n\n" + router_line + "\n"

text = text.replace('"0.8.0"', '"0.8.2"')
text = text.replace("'0.8.0'", "'0.8.2'")
text = text.replace('"0.8.1"', '"0.8.2"')
text = text.replace("'0.8.1'", "'0.8.2'")

path.write_text(text, encoding="utf-8")

print("MAIN.PY: REPAIRED")
print("VERSION: 0.8.2")
