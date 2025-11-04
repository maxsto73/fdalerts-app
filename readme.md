# ⚽ FDAlerts App

Flask εφαρμογή για αποστολή SMS (Yuboto OMNI) με landing link. Τρέχει είτε σε Raspberry / Synology με Docker, είτε μέσα από Portainer.

---

## 1. Εγκατάσταση σε **Raspberry Pi** ή **Synology** μέσω **SSH**

### 1.1 Προαπαιτούμενα
- Εγκατεστημένο **Docker** και **docker compose**
- Ένας φάκελος π.χ. `/opt/fdalerts` ή σε Synology: `/volume1/docker/fdalerts`
- Πρόσβαση SSH

### 1.2 Κατέβασε το repo
```bash
mkdir -p /opt/fdalerts
cd /opt/fdalerts
git clone https://github.com/maxsto73/fdalerts-app.git .
(αν το έχεις ήδη, κάνεις:)

bash
Αντιγραφή κώδικα
cd /opt/fdalerts
git pull
1.3 Φτιάξε το .env
Δημιούργησε αρχείο .env δίπλα στο docker-compose.yml:

env
Αντιγραφή κώδικα
# Πόρτα που θα ακούει το Flask
PORT=8899

# Yuboto OMNI ρυθμίσεις
SMS_PROVIDER=omni
YUBOTO_API_KEY=MDBCNDZFQTktREI1MS00NUMxLUEzRTktOTY3RTQ0NURGNjA1
SMS_SENDER=FDTeam 2012

# Για τα links που στέλνει με sms
PUBLIC_BASE_URL=http://192.168.1.241:8899
# Αν θες και domain όταν το σηκώνεις στο Synology reverse proxy:
SECOND_PUBLIC_BASE_URL=https://app.fdteam2012.gr
👉 Η εφαρμογή μπορεί να διαβάζει και τις δύο (PUBLIC_BASE_URL και SECOND_PUBLIC_BASE_URL) και να διαλέγεις ποια θα χρησιμοποιείς αργότερα μέσα από το app.

1.4 Δημιούργησε docker-compose.yml
yaml
Αντιγραφή κώδικα
version: "3.9"

services:
  fdalerts:
    image: python:3.11-slim
    container_name: fdalerts
    working_dir: /app
    env_file:
      - .env
    ports:
      - "${PORT:-8899}:8899"
    volumes:
      # ο κώδικας από το repo
      - ./app:/app
      # logs / data κλπ
      - ./data:/app/data
    command: >
      bash -c "
        apt update &&
        apt install -y git &&
        git clone https://github.com/maxsto73/fdalerts-app.git . || true &&
        pip install --no-cache-dir -r requirements.txt &&
        python3 app.py
      "
    restart: unless-stopped
Τι κάνει αυτό:

ανοίγει την πόρτα 8899 προς τα έξω

κατεβάζει το repo μέσα στο container

εγκαθιστά Flask + requests

τρέχει το app.py

1.5 Εκκίνηση
bash
Αντιγραφή κώδικα
docker compose up -d
Δες ότι τρέχει:

bash
Αντιγραφή κώδικα
docker ps
docker logs -f fdalerts
Άνοιξε:

http://IP_TOU_PI:8899
ή (αν έχεις βάλει reverse proxy)

https://app.fdteam2012.gr

2. Εγκατάσταση μέσω Portainer
Αυτό είναι για Synology ή οπουδήποτε έχεις Portainer.

2.1 Ετοίμασε έναν φάκελο στο NAS
Π.χ.

/volume1/docker/fdalerts/app

/volume1/docker/fdalerts/data

(σημαντικό: να υπάρχουν, γιατί το compose θα τα κάνει bind)

2.2 Φτιάξε ένα .env στο NAS
Φτιάξε αρχείο /volume1/docker/fdalerts/.env με:

env
Αντιγραφή κώδικα
PORT=8899
SMS_PROVIDER=omni
YUBOTO_API_KEY=MDBCNDZFQTktREI1MS00NUMxLUEzRTktOTY3RTQ0NURGNjA1
SMS_SENDER=FDTeam 2012
PUBLIC_BASE_URL=http://192.168.1.241:8899
SECOND_PUBLIC_BASE_URL=https://app.fdteam2012.gr
2.3 Άνοιξε Portainer → Stacks → Add Stack
Δώσε όνομα π.χ. fdalerts και βάλε αυτό το YAML:

yaml
Αντιγραφή κώδικα
version: "3.9"

services:
  fdalerts:
    image: python:3.11-slim
    container_name: fdalerts
    working_dir: /app
    env_file:
      - /data/compose/{{.Stack.ID}}/.env
    ports:
      - "8899:8899"
    volumes:
      # προσαρμόζεις τα paths σου στο Synology
      - /volume1/docker/fdalerts/app:/app
      - /volume1/docker/fdalerts/data:/app/data
    command: >
      bash -c "
        apt update &&
        apt install -y git &&
        cd /app &&
        git clone https://github.com/maxsto73/fdalerts-app.git . || true &&
        pip install --no-cache-dir -r requirements.txt &&
        python3 app.py
      "
    restart: unless-stopped
🔴 Αν το Portainer σου παραπονιέται ότι δεν βρίσκει το .env στο /data/compose/..., τότε απλά βάλε το πλήρες path του NAS σου:

yaml
Αντιγραφή κώδικα
env_file:
  - /volume1/docker/fdalerts/.env
2.4 Deploy
Πατάς Deploy the stack.
Μετά δες τα logs από το container fdalerts για να σιγουρευτείς ότι κατέβηκε το repo και ξεκίνησε ο Flask.

🟣 Σημειώσεις
Αν δεν βλέπεις favicon, βεβαιώσου ότι ο φάκελος static/ υπάρχει μέσα στο bind mount (/volume1/docker/fdalerts/app/static).

Αν το landing link ανοίγει σε 127.0.0.1, τότε στο .env βάλε την κανονική public διεύθυνση και κάνε docker compose restart.

Αν θες να αλλάξεις πόρτα, άλλαξε το PORT= στο .env και το mapping στο compose.







