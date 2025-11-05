#!/usr/bin/env python3
import json
import os
from pathlib import Path
from flask import Flask, render_template, request
import requests

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CONTACTS_FILE = DATA_DIR / "contacts.json"
LOG_FILE = DATA_DIR / "logs.json"

PORT = int(os.getenv("PORT", 8899))
SMS_PROVIDER = os.getenv("SMS_PROVIDER", "omni")
YUBOTO_API_KEY = os.getenv("YUBOTO_API_KEY", "")
SMS_SENDER = os.getenv("SMS_SENDER", "FDTeam 2012")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", f"http://127.0.0.1:{PORT}")

app = Flask(__name__, static_folder=str(BASE_DIR / "static"))

# --- Helpers ---
def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def send_sms(numbers, text):
    """Send SMS via Yuboto OMNI API"""
    if not YUBOTO_API_KEY:
        return False, {"error": "Missing YUBOTO_API_KEY"}
    payload = {
        "dlr": False,
        "contacts": [{"phonenumber": n} for n in numbers],
        "sms": {
            "sender": SMS_SENDER,
            "text": text,
            "validity": 180,
            "typesms": "sms",
            "longsms": False,
            "priority": 1
        }
    }
    try:
        resp = requests.post(
            "https://services.yuboto.com/omni/v1/Send",
            headers={
                "Authorization": f"Basic {YUBOTO_API_KEY}",
                "Content-Type": "application/json; charset=utf-8"
            },
            json=payload,
            timeout=30
        )
        ok = 200 <= resp.status_code < 300
        return ok, resp.text
    except Exception as e:
        return False, str(e)

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    contacts = load_json(CONTACTS_FILE, [])
    logs = load_json(LOG_FILE, [])

    if request.method == "POST":
        channel = request.form.get("channel")
        message = request.form.get("message", "").strip()
        selected_contacts = request.form.getlist("contacts")

        if channel == "sms" and selected_contacts:
            ok, result = send_sms(selected_contacts, message)
            logs.append({
                "channel": "sms",
                "contacts": selected_contacts,
                "message": message,
                "result": result
            })
            save_json(LOG_FILE, logs)
            return render_template(
                "index.html", 
                port=PORT, version="v1.0", 
                sms_provider=SMS_PROVIDER, 
                status=("✅ Μήνυμα στάλθηκε!" if ok else "❌ Αποτυχία αποστολής"), 
                ok=ok, 
                contacts=contacts, logs=logs
            )

    return render_template(
        "index.html", port=PORT, version="v1.0",
        sms_provider=SMS_PROVIDER, contacts=contacts,
        logs=logs
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
