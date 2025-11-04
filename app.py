#!/usr/bin/env python3
import os
import json
import time
import base64
import uuid
from pathlib import Path
from datetime import datetime
import requests
from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    redirect,
    abort,
    make_response,
)

# -------------------------------------------------
# Paths / config
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

MESSAGES_FILE = DATA_DIR / "messages.json"
LOG_FILE = DATA_DIR / "logs.json"

# -------------------------------------------------
# Env / provider defaults
# -------------------------------------------------
# θα προσπαθήσει από .env / περιβάλλον
SMS_API_KEY = os.getenv(
    "SMS_API_KEY",
    # fallback στο κλειδί που δοκίμασες
    "MDBCNDZFQTktREI1MS00NUMxLUEzRTktOTY3RTQ0NURGNjA1",
)
SMS_SENDER = os.getenv("SMS_SENDER", "FDTeam 2012")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8899").rstrip("/")
PORT = int(os.getenv("PORT", "8899"))

YUBOTO_ENDPOINT = "https://services.yuboto.com/omni/v1/Send"

app = Flask(__name__, static_folder=str(BASE_DIR / "static"))

# -------------------------------------------------
# Helpers
# -------------------------------------------------


def _read_json(path: Path, default):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except Exception:
        return default


def _write_json(path: Path, data):
    # απλό write σε tmp + rename για να μην κολλάει
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def log_entry(entry: dict):
    logs = _read_json(LOG_FILE, [])
    logs.insert(0, entry)
    # κράτα μέχρι 200
    logs = logs[:200]
    try:
        _write_json(LOG_FILE, logs)
    except PermissionError:
        # αν δεν έχει δικαιώματα απλά το αγνοούμε
        pass


def load_messages():
    msgs = _read_json(MESSAGES_FILE, {})
    return msgs


def save_messages(msgs: dict):
    _write_json(MESSAGES_FILE, msgs)


def send_yuboto_omni(numbers, text, sender):
    """
    POST https://services.yuboto.com/omni/v1/Send
    Authorization: Basic <api_key>
    """
    if not SMS_API_KEY:
        return False, {"error": "Missing SMS_API_KEY"}

    contacts = [{"phonenumber": n} for n in numbers]
    payload = {
        "dlr": False,
        "contacts": contacts,
        "sms": {
            "sender": sender,
            "text": text,
            "validity": 180,
            "typesms": "sms",
            "longsms": False,
            "priority": 1,
        },
    }

    try:
        resp = requests.post(
            YUBOTO_ENDPOINT,
            headers={
                "Authorization": f"Basic {SMS_API_KEY}",
                "Content-Type": "application/json; charset=utf-8",
            },
            json=payload,
            timeout=30,
        )
        ok = 200 <= resp.status_code < 300
        try:
            data = resp.json()
        except Exception:
            data = {"raw": resp.text}
        return ok, {"status_code": resp.status_code, "response": data}
    except Exception as e:
        return False, {"exception": str(e)}


# -------------------------------------------------
# HTML (dark) – με extra πεδίο ελεύθερου sms
# -------------------------------------------------
INDEX_HTML = r"""
<!doctype html>
<html lang="el">
<head>
  <meta charset="utf-8" />
  <title>FD Alerts</title>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <link rel="icon" href="/static/favicon.ico">
  <style>
    :root {
      --bg: #0f172a;
      --panel: #1e293b;
      --panel2: #111827;
      --accent: #38bdf8;
      --accent2: #0ea5e9;
      --text: #e2e8f0;
      --muted: #94a3b8;
      --danger: #f43f5e;
      --radius: 14px;
    }
    * { box-sizing: border-box; }
    body {
      margin:0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top, #0f172a 0%, #020617 60%);
      color: var(--text);
      min-height:100vh;
      display:flex;
      flex-direction:column;
    }
    header {
      background: rgba(15,23,42,0.7);
      backdrop-filter: blur(6px);
      border-bottom: 1px solid rgba(148,163,184,0.1);
      padding: 14px 18px;
      display:flex; align-items:center; gap:10px;
    }
    header img {
      width: 28px; height:28px;
    }
    .title {
      font-weight:600;
      letter-spacing: -0.01em;
    }
    main {
      display:flex;
      gap:18px;
      padding:18px;
      flex:1;
      align-items:flex-start;
    }
    .card {
      background: radial-gradient(circle at top, #1f2937 0%, #0f172a 70%);
      border: 1px solid rgba(148,163,184,0.1);
      border-radius: var(--radius);
      padding: 16px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.25);
    }
    .left { flex: 2; display:flex; flex-direction:column; gap:16px; }
    .right { flex: 1; display:flex; flex-direction:column; gap:16px; }
    label {
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
      margin-bottom: 4px;
      display:block;
    }
    input, select, textarea {
      width:100%;
      background: rgba(15,23,42,0.3);
      border: 1px solid rgba(148,163,184,0.08);
      border-radius: 10px;
      padding: 8px 10px;
      color: var(--text);
      font-size: 0.9rem;
      outline:none;
    }
    input:focus, select:focus, textarea:focus {
      border-color: rgba(56,189,248,0.7);
      background: rgba(15,23,42,0.6);
    }
    textarea { min-height: 90px; resize: vertical; }
    button {
      background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
      border:none;
      border-radius: 9999px;
      color: #0f172a;
      font-weight:600;
      padding: 9px 16px;
      cursor:pointer;
      display:inline-flex;
      gap:6px;
      align-items:center;
    }
    .btn-secondary {
      background: rgba(15,23,42,0.3);
      border: 1px solid rgba(148,163,184,0.1);
      color: var(--text);
    }
    .flex { display:flex; gap:10px; }
    .flex-col { display:flex; flex-direction:column; gap:8px; }
    .w-50 { width:50%; }
    .logs-list {
      max-height: 280px;
      overflow-y:auto;
    }
    .log-item {
      border-bottom: 1px solid rgba(148,163,184,0.04);
      padding:6px 0;
      font-size:0.75rem;
    }
    .badge {
      background: rgba(148,163,184,0.12);
      padding:2px 6px;
      border-radius:9999px;
      font-size:0.62rem;
      text-transform:uppercase;
      letter-spacing:0.04em;
    }
    @media (max-width: 900px) {
      main { flex-direction:column; }
      .left,.right { width:100%; }
      .flex { flex-direction:column; }
      .w-50 { width:100%; }
    }
  </style>
</head>
<body>
  <header>
    <img src="/static/icons/logo_final.png" alt="logo" onerror="this.style.display='none'">
    <div>
      <div class="title">FD Alerts</div>
      <div style="font-size:0.65rem; color:var(--muted)">Υπενθυμίσεις ομάδας • SMS μέσω Yuboto OMNI</div>
    </div>
  </header>
  <main>
    <div class="left">
      <form id="sendForm" action="/send" method="post" enctype="multipart/form-data" class="card">
        <h2 style="margin-top:0; font-size:1rem;">📤 Αποστολή SMS</h2>

        <div class="flex">
          <div class="w-50 flex-col">
            <label for="sender">Αποστολέας</label>
            <input id="sender" name="sender" value="{{ sender }}" />
          </div>
          <div class="w-50 flex-col">
            <label for="date">Ημερομηνία</label>
            <input id="date" name="date" type="date" value="{{ today }}" />
          </div>
        </div>

        <div class="flex">
          <div class="w-50 flex-col">
            <label for="time">Ώρα</label>
            <input id="time" name="time" type="time" value="20:45" />
          </div>
          <div class="w-50 flex-col">
            <label for="template">Template</label>
            <select id="template" name="template">
              <option value="">-- Επέλεξε --</option>
              {% for mid, mtext in messages.items() %}
              <option value="{{ mid }}">{{ mtext[:60].replace('\n',' ') }}...</option>
              {% endfor %}
            </select>
          </div>
        </div>

        <div class="flex-col">
          <label for="linkid">Landing Link</label>
          <input id="linkid" name="linkid" placeholder="(προαιρετικό) id για /r?id=..." />
          <small style="color:var(--muted); font-size:0.65rem;">
            Αν δώσεις id, το sms θα δείχνει: {{ public_base }}/r?id=&lt;id&gt;
          </small>
        </div>

        <div class="flex-col">
          <label for="numbers">Τηλέφωνα (ένα ανά γραμμή)</label>
          <textarea id="numbers" name="numbers" placeholder="+3069..., 69..., 003069..."></textarea>
        </div>

        <div class="flex-col">
          <label for="csv">ή ανέβασμα CSV (1 στήλη με αριθμούς)</label>
          <input id="csv" name="csv" type="file" accept=".csv,text/csv" />
        </div>

        <div class="flex-col">
          <label for="free_sms">✉️ Ελεύθερο SMS (αν το συμπληρώσεις, αυτό θα σταλεί)</label>
          <textarea id="free_sms" name="free_sms" placeholder="Γράψε εδώ μήνυμα που θα σταλεί αυτούσιο..."></textarea>
        </div>

        <div style="margin-top:12px; display:flex; gap:10px;">
          <button type="submit">📨 Αποστολή</button>
          <button type="reset" class="btn-secondary">Καθαρισμός</button>
        </div>
      </form>
    </div>
    <div class="right">
      <div class="card">
        <h3 style="margin-top:0; font-size:0.95rem;">🧾 Πρόσφατα logs</h3>
        <div id="logs" class="logs-list">
          {% for log in logs %}
          <div class="log-item">
            <div><span class="badge">{{ log.timestamp }}</span></div>
            <div>{{ log.message }}</div>
            {% if log.recipients %}<div style="color:var(--muted)">➡ {{ ", ".join(log.recipients) }}</div>{% endif %}
            {% if log.provider %}<div style="color:var(--muted); font-size:0.65rem;">{{ log.provider }}</div>{% endif %}
          </div>
          {% endfor %}
        </div>
      </div>
      <div class="card">
        <h3 style="margin-top:0; font-size:0.9rem;">ℹ️ Info</h3>
        <p style="font-size:0.75rem; color:var(--muted);">
          Provider: Yuboto OMNI<br>
          Endpoint: <code style="font-size:0.62rem;">/omni/v1/Send</code><br>
          Base URL: <code style="font-size:0.62rem;">{{ public_base }}</code>
        </p>
      </div>
    </div>
  </main>
</body>
</html>
"""

# -------------------------------------------------
# Routes
# -------------------------------------------------


@app.route("/")
def index():
    messages = load_messages()
    logs = _read_json(LOG_FILE, [])
    today = datetime.now().strftime("%Y-%m-%d")
    html = INDEX_HTML.replace("{{ sender }}", SMS_SENDER)
    html = html.replace("{{ today }}", today)
    html = html.replace("{{ public_base }}", PUBLIC_BASE_URL)

    # Jinja-like render for messages/logs
    # για να μην βάζουμε πραγματικό Jinja εδώ, θα κάνουμε ένα μικρό fake
    from jinja2 import Template

    t = Template(INDEX_HTML)
    return t.render(
        sender=SMS_SENDER,
        today=today,
        public_base=PUBLIC_BASE_URL,
        messages=messages,
        logs=logs,
    )


@app.route("/send", methods=["POST"])
def api_send():
    messages = load_messages()

    sender = request.form.get("sender") or SMS_SENDER
    template_id = request.form.get("template") or ""
    date_str = request.form.get("date") or ""
    time_str = request.form.get("time") or ""
    link_id = request.form.get("linkid") or ""
    numbers_raw = request.form.get("numbers") or ""
    free_sms = request.form.get("free_sms") or ""

    # collect numbers
    numbers = []
    for line in numbers_raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # normalize
        if line.startswith("00"):
            line = line[2:]
        if line.startswith("30") and not line.startswith("+"):
            line = "+" + line
        if line.startswith("69") and not line.startswith("+30"):
            line = "+30" + line
        numbers.append(line)

    # CSV
    if "csv" in request.files and request.files["csv"].filename:
        f = request.files["csv"]
        content = f.read().decode("utf-8", errors="ignore")
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("00"):
                line = line[2:]
            if line.startswith("30") and not line.startswith("+"):
                line = "+" + line
            if line.startswith("69") and not line.startswith("+30"):
                line = "+30" + line
            numbers.append(line)

    numbers = list(dict.fromkeys(numbers))  # dedupe

    # build message
    if free_sms.strip():
        final_msg = free_sms.strip()
    else:
        base_msg = messages.get(template_id, "").replace("\\n", "\n")
        # κάνε μικρές αντικαταστάσεις αν θες
        final_msg = base_msg
        if date_str:
            final_msg = final_msg.replace("2025-10-27", date_str)
        if time_str:
            final_msg = final_msg.replace("20:45", time_str)
        if link_id:
            final_msg += f"\n👉 Δες περισσότερα: {PUBLIC_BASE_URL}/r?id={link_id}"

    ok = False
    provider_info = {}
    if numbers:
        ok, provider_info = send_yuboto_omni(numbers, final_msg, sender)

    log_entry(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": final_msg,
            "recipients": numbers,
            "provider": "yuboto_omni",
            "provider_info": provider_info,
            "ok": ok,
        }
    )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"ok": ok, "provider": provider_info})

    if ok:
        return redirect("/")
    else:
        return make_response("Provider error", 500)


@app.route("/api/get_logs")
def api_get_logs():
    logs = _read_json(LOG_FILE, [])
    return jsonify(logs)


@app.route("/r")
def landing():
    mid = request.args.get("id", "")
    messages = load_messages()
    txt = messages.get(mid, "Μήνυμα δεν βρέθηκε.")
    return f"<html><body><h3>FD Alerts</h3><pre>{txt}</pre></body></html>"


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(str(BASE_DIR / "static"), filename)


# -------------------------------------------------
# main
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
