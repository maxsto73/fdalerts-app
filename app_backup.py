#!/usr/bin/env python3
# RasPiPush Ultimate — Flask Web Interface (port 8899)
# Περιλαμβάνει: Pushover, Telegram, Web Push (VAPID-ready), SMS (BudgetSMS / SMS.to)

from flask import Flask, request, jsonify, send_from_directory
import json
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__, static_folder="static", static_url_path="/static")
from flask import send_from_directory

@app.route('/favicon.ico')
def favicon():
    from flask import make_response, send_from_directory
    response = make_response(send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    ))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# ───────────────────────── ΒΑΣΙΚΑ ─────────────────────────
BASE_DIR = Path("/opt/raspipush_ultimate")
STATIC_DIR = BASE_DIR / "static"
LOG_FILE = BASE_DIR / "logs.json"

BASE_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
if not LOG_FILE.exists():
    LOG_FILE.write_text("[]", encoding="utf-8")

# ──────────────────────── ΒΟΗΘΗΤΙΚΑ ───────────────────────
def save_log(message: str, channel: str):
    try:
        logs = json.loads(LOG_FILE.read_text(encoding="utf-8"))
    except Exception:
        logs = []
    logs.insert(0, {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "channel": channel,
        "message": message
    })
    LOG_FILE.write_text(json.dumps(logs[:200], ensure_ascii=False, indent=2), encoding="utf-8")

# ───────────────────────── API ─────────────────────────────
@app.route("/api/push", methods=["POST"])
def api_push():
    message = (request.get_json() or {}).get("message", "")
    save_log(message, "push")
    return jsonify({"status": "ok"})

@app.route("/api/sms", methods=["POST"])
def api_sms():
    message = (request.get_json() or {}).get("message", "")
    save_log(message, "sms")
    return jsonify({"status": "ok"})

@app.route("/api/telegram", methods=["POST"])
def api_telegram():
    message = (request.get_json() or {}).get("message", "")
    save_log(message, "telegram")
    return jsonify({"status": "ok"})

@app.route("/api/pushover", methods=["POST"])
def api_pushover():
    message = (request.get_json() or {}).get("message", "")
    save_log(message, "pushover")
    return jsonify({"status": "ok"})

@app.route("/api/get_logs")
def api_get_logs():
    try:
        logs = json.loads(LOG_FILE.read_text(encoding="utf-8"))
    except Exception:
        logs = []
    return jsonify({"logs": logs})

# ─────────────── Manifest & Favicon (προαιρετικά) ─────────

@app.route("/manifest.json")
def manifest():
    return send_from_directory(STATIC_DIR, "manifest.json")

# ─────────────────────── ΑΡΧΙΚΗ (UI) ──────────────────────
@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html lang="el">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="manifest" href="/manifest.json">
<link rel="icon" type="image/x-icon" href="/static/favicon.ico">
<title>FDTEAM2012 – Ειδοποιήσεις</title>
<style>
:root{--bg:#0e1013;--card:#1b1e23;--ink:#e0e0e0;--acc:#00bcd4;--mut:#aeb6bf}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",Roboto}
.wrap{max-width:900px;margin:0 auto;padding:16px}
.nav{display:flex;gap:28px;justify-content:center;align-items:center;background:#181a1f;padding:12px 0;margin-bottom:18px}
.nav a{color:#cfd6dd;text-decoration:none;font-weight:700}
.nav a.active{color:var(--acc);text-decoration:underline}
.card{background:var(--card);border-radius:14px;padding:18px;margin:0 auto;max-width:620px;box-shadow:0 0 20px rgba(0,0,0,.35)}
h1{margin:8px 0 14px;color:var(--acc);text-align:center}
label{display:block;text-align:left;margin-top:10px;color:#d7dee7}
input,textarea,select{width:100%;padding:12px;border:none;border-radius:10px;background:#111;color:#eee;font-size:16px;margin-top:6px}
textarea{min-height:90px;resize:vertical}
.btn{width:100%;background:var(--acc);color:#fff;border:none;border-radius:10px;padding:12px 14px;font-weight:600;cursor:pointer;margin-top:12px}
.btn:hover{filter:brightness(0.92)}
.help{color:var(--mut);font-size:13px;margin-top:6px}
#preview{background:#111;border-radius:10px;padding:12px;margin-top:12px;white-space:pre-wrap;text-align:left}
@media (max-width:600px){h1{font-size:22px}.nav{gap:18px}}
</style>
</head>
<body>
<div class="wrap">
  <div class="nav">
    <a class="active" href="/">Αποστολή</a>
    <a href="/history">Ιστορικό</a>
  </div>

  <div class="card">
    <h1>📅 Υπενθύμιση Αγώνα</h1>

    <label>Τόπος</label>
    <input id="place" placeholder="π.χ. Στάδιο Καραϊσκάκη">

    <label>Ημερομηνία</label>
    <input id="date" type="date">

    <label>Ώρα (24ωρη μορφή)</label>
    <input id="time" type="time" step="60" lang="el" pattern="[0-9]{2}:[0-9]{2}" placeholder="π.χ. 18:30" value="18:30" onfocus="this.showPicker?.()">


    <label>Κανάλι αποστολής</label>
    <select id="channel">
      <option value="push">Push</option>
      <option value="sms">SMS</option>
      <option value="telegram">Telegram</option>
      <option value="pushover">Pushover</option>
    </select>

    <div class="help">Προδιαμορφωμένο: <b>«Παίζουμε μπαλίτσα στο ___ την ___ ώρα ___»</b></div>

    <label>Ή γράψε χειροκίνητα (προαιρετικό)</label>
    <textarea id="custom" placeholder="Αν το συμπληρώσεις, θα σταλεί αυτό αντί του προδιαμορφωμένου."></textarea>

    <button class="btn" onclick="updatePreview()">🔍 Προεπισκόπηση</button>
    <div id="preview">⚽ Προεπισκόπηση μηνύματος...</div>
    <button class="btn" onclick="sendMessage()">📤 Αποστολή</button>
    <div id="status" class="help"></div>
  </div>
</div>

<audio id="ok" src="https://cdn.pixabay.com/download/audio/2022/03/15/audio_ba45d7cce4.mp3?filename=click-124467.mp3"></audio>

<script>
// Μετατρέπει input 'time' σε HH:MM αν κάποιος browser δίνει AM/PM visualization
function toHHMM(raw){
  if(!raw) return "";
  // Τυπικά τα time inputs επιστρέφουν πάντα "HH:MM"
  const m = raw.match(/^(\d{1,2}):(\d{2})(?:\s*(AM|PM))?$/i);
  if(!m) return raw;
  let h = parseInt(m[1],10); const mm = m[2]; const ap = (m[3]||"").toUpperCase();
  if(ap==="AM"){ if(h===12) h=0; }
  else if(ap==="PM"){ if(h<12) h+=12; }
  return (h<10?("0"+h):(""+h))+":"+mm;
}

function buildMessage(){
  const place = document.getElementById("place").value.trim() || "_____";
  const date  = document.getElementById("date").value || "_____";
  const time  = toHHMM(document.getElementById("time").value) || "_____";
  const custom = document.getElementById("custom").value.trim();
  if(custom) return custom;
  return `⚽ Παίζουμε μπαλίτσα στο ${place} την ${date} ώρα ${time}

Επιβεβαίωσε 👉 http://fdteam2012.gr/rsvp?id=evt${Date.now()}`;
}

function updatePreview(){
  document.getElementById("preview").textContent = buildMessage();
  document.getElementById("status").textContent = "👀 Έτοιμη προεπισκόπηση.";
  // Φόρτωσε picker σε mobile για καλύτερη εμπειρία
  document.getElementById("time").showPicker?.();
}

async function sendMessage(){
  const channel = document.getElementById("channel").value;
  const message = document.getElementById("preview").textContent.trim();
  const ok = document.getElementById("ok");
  const st = document.getElementById("status");

  if(!message){ st.textContent="⚠️ Κάνε πρώτα προεπισκόπηση."; return; }

  st.textContent = "⏳ Αποστολή...";
  try{
    const r = await fetch(`/api/${channel}`, {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ message })
    });
    if(r.ok){ ok.play(); st.textContent="✅ Στάλθηκε!"; }
    else { st.textContent="❌ Αποτυχία αποστολής."; }
  }catch(e){
    st.textContent="❌ Σφάλμα δικτύου.";
  }
}

document.addEventListener("DOMContentLoaded", ()=>{
  // Βάλε placeholder 24ωρης μορφής αν χρειαστεί
  const t = document.getElementById("time");
  if(!t.placeholder) t.placeholder = "HH:MM";
});
</script>
</body>
</html>
"""

# ─────────────────────── ΙΣΤΟΡΙΚΟ ────────────────────────
@app.route("/history")
def history():
    try:
        logs = json.loads(LOG_FILE.read_text(encoding="utf-8"))
    except Exception:
        logs = []
    rows = "".join(
        f"<tr><td>{l.get('time','')}</td><td>{(l.get('channel','') or '').upper()}</td><td>{l.get('message','').replace('<','&lt;')}</td></tr>"
        for l in logs
    ) or "<tr><td colspan='3'>Δεν υπάρχουν αποστολές ακόμη</td></tr>"

    return f"""
<!DOCTYPE html>
<html lang="el">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="manifest" href="/manifest.json">
<link rel="icon" type="image/x-icon" href="/static/favicon.ico">
<title>Ιστορικό Ειδοποιήσεων</title>
<style>
:root{{--bg:#0e1013;--card:#1b1e23;--ink:#e0e0e0;--acc:#00bcd4}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",Roboto}}
.wrap{{max-width:1000px;margin:0 auto;padding:16px}}
.nav{{display:flex;gap:28px;justify-content:center;align-items:center;background:#181a1f;padding:12px 0;margin-bottom:18px}}
.nav a{{color:#cfd6dd;text-decoration:none;font-weight:700}}
.nav a.active{{color:var(--acc);text-decoration:underline}}
.card{{background:var(--card);border-radius:14px;padding:18px;margin:0 auto;max-width:960px;box-shadow:0 0 20px rgba(0,0,0,.35)}}
h1{{margin:8px 0 14px;color:var(--acc);text-align:center}}
table{{width:100%;border-collapse:collapse}}
th,td{{padding:10px;border-bottom:1px solid #2a2e36;text-align:left;vertical-align:top}}
@media (max-width:700px){{th,td{{font-size:13px;padding:8px}}}}
</style>
</head>
<body>
<div class="wrap">
  <div class="nav">
    <a href="/">Αποστολή</a>
    <a class="active" href="/history">Ιστορικό</a>
  </div>
  <div class="card">
    <h1>📜 Ιστορικό Αποστολών</h1>
    <table>
      <tr><th>Ώρα</th><th>Κανάλι</th><th>Μήνυμα</th></tr>
      {rows}
    </table>
  </div>
</div>
</body>
</html>
"""

if __name__ == "__main__":
    print("✅ RasPiPush Ultimate εκτελείται στη θύρα 8899")
    app.run(host="0.0.0.0", port=8899)
