#!/bin/bash
set -e

echo "======================================="
echo " 🚀 FD Alerts Automatic Installer"
echo "======================================="

APP_DIR="/opt/raspipush_ultimate"
SERVICE_NAME="fdalerts.service"
REPO_URL="https://github.com/maxsto73/fdalerts-app/archive/refs/heads/main.zip"

# ------------------------------------------
# Καθαρισμός παλιάς εγκατάστασης
# ------------------------------------------
echo "🧹 Καθαρισμός παλιάς εγκατάστασης..."
sudo systemctl stop $SERVICE_NAME >/dev/null 2>&1 || true
sudo systemctl disable $SERVICE_NAME >/dev/null 2>&1 || true
sudo rm -rf $APP_DIR
sudo mkdir -p $APP_DIR
sudo chown -R pi:pi $APP_DIR

# ------------------------------------------
# Κατέβασμα νέας έκδοσης
# ------------------------------------------
echo "⬇️  Κατεβάζω την τελευταία έκδοση από GitHub..."
cd /tmp
sudo rm -f app.zip
sudo curl -L $REPO_URL -o app.zip
sudo unzip -oq app.zip
sudo mv fdalerts-app-main/* $APP_DIR/
sudo rm -rf fdalerts-app-main app.zip
sudo chown -R pi:pi $APP_DIR

# ------------------------------------------
# Δημιουργία .env αν δεν υπάρχει
# ------------------------------------------
if [ ! -f "$APP_DIR/.env" ]; then
  echo "🧩 Δημιουργία αρχείου .env..."
  cat <<EOF | sudo tee $APP_DIR/.env >/dev/null
SMS_API_KEY=your_api_key_here
SMS_PROVIDER=provider_name_here
EOF
  sudo chown pi:pi $APP_DIR/.env
fi

# ------------------------------------------
# Δημιουργία Python venv και εγκατάσταση dependencies
# ------------------------------------------
echo "🐍 Δημιουργία Python virtual environment..."
sudo apt update -y >/dev/null 2>&1
sudo apt install -y python3 python3-venv python3-pip unzip >/dev/null 2>&1
sudo -u pi python3 -m venv $APP_DIR/venv
sudo -u pi $APP_DIR/venv/bin/pip install --break-system-packages flask requests python-dotenv >/dev/null

# ------------------------------------------
# Δημιουργία systemd service
# ------------------------------------------
echo "⚙️  Δημιουργία systemd service..."
sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME" <<EOF
[Unit]
Description=FD Alerts Flask Service on port 8899
After=network.target

[Service]
User=pi
WorkingDirectory=$APP_DIR
Environment=FLASK_APP=app.py
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# ------------------------------------------
# Εκκίνηση υπηρεσίας
# ------------------------------------------
echo "🔁 Ενεργοποίηση υπηρεσίας..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

sleep 3

# ------------------------------------------
# Έλεγχος λειτουργίας
# ------------------------------------------
if systemctl is-active --quiet $SERVICE_NAME; then
  echo ""
  echo "✅ Εγκατάσταση ολοκληρώθηκε επιτυχώς!"
  echo "🌐 Άνοιξε: http://$(hostname -I | awk '{print $1}'):8899"
else
  echo ""
  echo "⚠️ Το service δεν ξεκίνησε σωστά. Δες logs με:"
  echo "   sudo journalctl -u $SERVICE_NAME -n 30 --no-pager"
fi
