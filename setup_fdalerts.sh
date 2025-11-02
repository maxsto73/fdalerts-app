#!/bin/bash
set -e

echo "======================================="
echo " 🚀 FD Alerts — Full Auto Installer"
echo "======================================="

APP_DIR="/opt/raspipush_ultimate"
SERVICE_NAME="fdalerts.service"
REPO_URL="https://github.com/maxsto73/fdalerts-app/archive/refs/heads/main.zip"
TMP_DIR="/tmp/fdalerts-app"

echo "🧹 Καθαρισμός παλιάς εγκατάστασης..."
sudo systemctl stop $SERVICE_NAME >/dev/null 2>&1 || true
sudo rm -rf "$APP_DIR" "$TMP_DIR" /etc/systemd/system/$SERVICE_NAME

echo "⬇️  Κατέβασμα τελευταίας έκδοσης..."
mkdir -p "$TMP_DIR"
cd /tmp
sudo curl -L -o app.zip "$REPO_URL"
sudo unzip -qo app.zip -d "$TMP_DIR"

echo "📦 Αντιγραφή αρχείων..."
sudo mkdir -p "$APP_DIR"
sudo cp -r $TMP_DIR/fdalerts-app-main/* "$APP_DIR/"
sudo chmod -R 755 "$APP_DIR"

if [ -f "$HOME/.env" ]; then
  echo "⚙️  Αντιγραφή τοπικού .env..."
  sudo cp "$HOME/.env" "$APP_DIR/.env"
else
  echo "⚠️  Δεν βρέθηκε .env — θα πρέπει να το δημιουργήσεις στο $APP_DIR/.env"
fi

echo "🐍 Ρύθμιση Python περιβάλλοντος..."
sudo apt update -y >/dev/null
sudo apt install -y python3 python3-pip python3-venv unzip >/dev/null

cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --break-system-packages -r requirements.txt || true
pip install --break-system-packages flask requests python-dotenv || true
deactivate

echo "🛠️ Δημιουργία systemd υπηρεσίας..."
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=FD Alerts Flask Service on port 8899
After=network.target

[Service]
User=pi
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/python3 $APP_DIR/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "🔁 Επανεκκίνηση υπηρεσίας..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

sleep 3
echo
sudo systemctl status $SERVICE_NAME -n 15 --no-pager || true

echo
echo "✅ Ολοκληρώθηκε! Άνοιξε στο browser:"
echo "   👉 http://$(hostname -I | awk '{print $1}'):8899"
echo
