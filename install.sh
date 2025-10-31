#!/usr/bin/env bash
set -e
APP_DIR="/opt/raspipush_ultimate"

echo "[1/10] Ενημέρωση πακέτων..."
sudo apt-get update -y

echo "[2/10] Εγκατάσταση Python3, venv, pip..."
sudo apt-get install -y python3 python3-venv python3-pip

echo "[3/10] Εξαρτήσεις για Web Push (κρυπτογράφηση)"
sudo apt-get install -y build-essential libffi-dev libssl-dev python3-dev

echo "[4/10] Αντιγραφή αρχείων στο ${APP_DIR} ..."
sudo mkdir -p "$APP_DIR"
sudo cp -r ./* "$APP_DIR"/

echo "[5/10] Δημιουργία virtual environment..."
sudo python3 -m venv "$APP_DIR/venv"

echo "[6/10] Εγκατάσταση Python packages..."
sudo "$APP_DIR/venv/bin/pip" install --upgrade pip
sudo "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

if [ ! -f "$APP_DIR/.env" ]; then
  echo "[7/10] Δημιουργία .env από το .env.example ..."
  sudo cp "$APP_DIR/.env.example" "$APP_DIR/.env"
  echo ">>> Ρύθμισε tokens/keys στο $APP_DIR/.env (Pushover/Telegram/SMS/WebPush)"
fi

echo "[8/10] Εγκατάσταση systemd service..."
sudo cp "$APP_DIR/raspipush_ultimate.service" /etc/systemd/system/raspipush_ultimate.service
sudo systemctl daemon-reload
sudo systemctl enable raspipush_ultimate.service
sudo systemctl restart raspipush_ultimate.service

echo "[9/10] (Προαιρετικό) Εγκατάσταση Caddy για HTTPS"
echo "    - Δες το GUIDE.md (DNS + Caddyfile)."

echo "[10/10] Ολοκληρώθηκε! Η εφαρμογή τρέχει στο http://<IP-του-Pi>:8899"
