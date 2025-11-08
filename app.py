#!/usr/bin/env python3
import os
import json
import uuid
from pathlib import Path
from datetime import datetime
import base64
from flask import Flask, request, render_template, jsonify, redirect, abort
import requests

# -------------------------------------------------
# ΒΑΣΙΚΕΣ ΡΥΘΜΙΣΕΙΣ / PATHS
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

CONTACTS_FILE = DATA_DIR / "contacts.json"
VIEWS_FILE = DATA_DIR / "views.json"
LOGS_FILE = DATA_DIR / "logs.json"

# φτιάξε τα αρχεία αν δεν υπάρχουν
for f in (CONTACTS_FILE, VIEWS_FILE, LOGS_FILE):
    if not f.exists():
        f.write_text("[]", encoding="utf-8")

# -------------------------------------------------
# ENV
# -------------------------------------------------
PORT = int(os.getenv("PORT", "8899"))
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", f"http://127.0.0.1:{PORT}").rstrip("/")
SMS_PROVIDER = os.getenv("SMS_PROVIDER", "omni")
YUBOTO_API_KEY = os.getenv("YUBOTO_API_KEY", "")
SMS_SENDER = os.getenv("SMS_SENDER", "FDTeam 2012")

app = Flask(__name__, static_folder=str(BASE_DIR / "static"), template_folder=str(BASE_DIR / "templates"))

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def _read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def _write_json(path: Path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)

def load_contacts(): return _read_json(CONTACTS_FILE, [])
def save_contacts(c): _write_json(CONTACTS_FILE, c)
def load_views(): return _read_json(VIEWS_FILE, [])
def add_view(e):
    v = load_views(); v.insert(0, e); _write_json(VIEWS_FILE, v[:100])
def load_logs(): return _read_json(LOGS_FILE, [])
def add_log(e):
    l = load_logs(); l.insert(0, e); _write_json(LOGS_FILE, l[:200])

# -------------------------------------------------
# SMS – Yuboto OMNI
# -------------------------------------------------
def send_sms_yuboto(msisdns, text, sender):
    if not YUBOTO_API_KEY:
        return False, {"error": "Missing YUBOTO_API_KEY"}
    contacts = [{"phonenumber": num.lstrip("+")} for num in msisdns]
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
            "https://services.yuboto.com/omni/v1/Send",
            headers={
                "Authorization": f"Basic {YUBOTO_API_KEY}",
                "Content-Type": "application/json; charset=utf-8",
            },
            json=payload,
            timeout=20,
        )
        ok = 200 <= resp.status_code < 300
        try:
            data = resp.json()
        except Exception:
            data = {"raw": resp.text}
        return ok, {"status": resp.status_code, "data": data}
    except Exception as e:
        return False, {"exception": str(e)}

# -------------------------------------------------
# ΡΟΥΤΕΣ
# -------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    contacts = load_contacts()
    views = load_views()
    logs = load_logs()
    return render_template(
        "index.html",
        port=PORT,
        sms_provider=SMS_PROVIDER,
        sender=SMS_SENDER,
        public_base_url=PUBLIC_BASE_URL,
        contacts=contacts,
        views=views,
        logs=logs,
    )

@app.route("/send", methods=["POST"])
def send():
    date_str = request.form.get("match_date", "").strip()
    time_str = request.form.get("match_time", "").strip()
    place = request.form.get("match_place", "").strip()
    recipients_raw = request.form.get("recipients", "").strip()
    custom_text = request.form.get("custom_text", "").strip()

    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]
    if not recipients:
        return jsonify({"ok": False, "error": "Δεν επιλέχθηκαν παραλήπτες"}), 400

    if custom_text:
        final_msg = custom_text
    else:
        date_part = date_str or "_____"
        time_part = time_str or "__:__"
        place_part = place or "_____"
        final_msg = f"⚽ Flying Dads Team υπενθύμιση!\nΠαίζουμε μπαλίτσα στο {place_part} την {date_part} ώρα {time_part}"

    # landing per recipient
    contacts = load_contacts()
    sent_list = []
    for phone in recipients:
        rid = uuid.uuid4().hex[:8]
        name = next((c["name"] for c in contacts if c["phone"] == phone), "Φίλε μας")
        landing_url = f"{PUBLIC_BASE_URL}/r?id={rid}"
        personalized = f"{final_msg}\n\n{landing_url}"
        ok, info = send_sms_yuboto([phone], personalized, SMS_SENDER)
        add_log({
            "ts": datetime.now().isoformat(timespec="seconds"),
            "recipient": phone,
            "name": name,
            "message": final_msg,
            "landing_id": rid,
            "landing_url": landing_url,
            "ok": ok,
            "provider_info": info
        })
        sent_list.append({"phone": phone, "ok": ok})

    return jsonify({"ok": True, "sent": sent_list})

@app.route("/contacts", methods=["GET", "POST"])
def contacts_view():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        contacts = data.get("contacts", [])
        save_contacts(contacts)
        return jsonify({"ok": True})
    contacts = load_contacts()
    return render_template("contacts.html", contacts=contacts)

@app.route("/api/contacts", methods=["GET"])
def api_contacts(): return jsonify(load_contacts())

@app.route("/api/contacts/save", methods=["POST"])
def api_contacts_save():
    data = request.get_json(silent=True) or {}
    contacts = data.get("contacts", [])
    save_contacts(contacts)
    return jsonify({"ok": True})

@app.route("/r")
def landing():
    rid = request.args.get("id", "").strip() or "unknown"
    # Αν υπάρχει στο log, φέρνουμε το όνομα
    logs = load_logs()
    name = next((x.get("name") for x in logs if x.get("landing_id") == rid), "Φίλε μας")
    return render_template("landing.html", rid=rid, name=name)

@app.route("/r/seen", methods=["POST"])
def landing_seen():
    data = request.get_json(silent=True) or {}
    rid = data.get("id", "unknown")
    name = data.get("name", "").strip() or "Άγνωστος"
    add_view({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "id": rid,
        "name": name,
    })
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
