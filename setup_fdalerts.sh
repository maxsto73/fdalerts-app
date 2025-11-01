#!/bin/bash
set -e

SERVICE_NAME="fdalerts.service"
INSTALL_DIR="/opt/raspipush_ultimate"
REPO_URL="https://github.com/maxsto73/fdalerts-app/archive/refs/heads/main.zip"
PYTHON_BIN=$(command -v python3 || true)

echo "======================================="
echo " 🚀 FD Alerts Automatic Installer"
echo "======================================="

# -------------------------------
# 1. Καθαρή εγκατάσταση φακέλου
# -------------------------------
echo "🧹 Καθαρισμός παλιάς εγκατάστασης..."
sudo systemctl stop $SERVICE_NAME >/dev/null 2>&1 || true
sudo rm -rf $INSTALL_DIR
sudo mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

# -------------------------------
# 2. Λήψη αρχείων από GitHub
# -------------------------------
echo "⬇️  Κατεβάζω την τελευταία έκδοση από GitHub..."
sudo apt update -y >/dev/null
sudo apt install -y unzip curl python3 python3-venv python3-pip >/dev/null
curl -L "$REPO_URL" -o app.zip
unzip -o app.zip >/dev/null
mv fdalerts-app-main/* $INSTALL_DIR
rm -rf fdalerts-app-main app.zip

# -------------------------------
# 3. Δημιουργία .env
# -------------------------------
echo "🧩 Δημιουργία αρχείου .env..."
cat <<EOF | sudo tee $INSTALL_DIR/.env >/dev/null
API_KEY=MDBCNDZFQTktREI1MS00NUMxLUEzRTktOTY3RTQ0NURGNjA1
SENDER=FDTeam 2012
PROVIDER_URL=https://services.yuboto.com/omni/v1/Send
PORT=8899
EOF

sudo chown pi:pi $INSTALL_DIR/.env
sudo chmod 600 $INSTALL_DIR/.env

# -------------------------------
# 4. Δημιουργία Python venv
# -------------------------------
echo "🐍 Δημιουργία Python virtual environment..."
$PYTHON_BIN -m venv venv
source venv/bin/activate
pip install --break-system-packages flask requests >/dev/null
deactivate

# -------------------------------
# 5. Δημιουργία systemd υπηρεσίας
# -------------------------------
echo "⚙️  Δημιουργία systemd service..."
sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME" <<EOF
[Unit]
Description=FD Alerts Flask Service on port 8899
After=network.target

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/app.py
EnvironmentFile=$INSTALL_DIR/.env
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF

# -------------------------------
# 6. Ενεργοποίηση και εκκίνηση
# -------------------------------
echo "🔁 Εκκίνηση υπηρεσίας..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME >/dev/null
sudo systemctl restart $SERVICE_NAME

sleep 3
if systemctl is-active --quiet $SERVICE_NAME; then
    echo ""
    echo "✅ Εγκατάσταση ολοκληρώθηκε επιτυχώς!"
    echo "🌐 Άνοιξε: http://$(hostname -I | awk '{print $1}'):8899"
else
    echo ""
    echo "⚠️ Το service δεν ξεκίνησε σωστά. Δες logs με:"
    echo "   sudo journalctl -u fdalerts.service -n 30 --no-pager"
fi

echo ""
