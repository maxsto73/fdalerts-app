[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)]()
[![Version](https://img.shields.io/badge/version-v2025.11-green)]()
[![Python](https://img.shields.io/badge/Python-3.11-yellow?logo=python)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey)]()

Flask-based SMS Automation System for FDTeam 2012 ⚽  
Τρέχει σε Raspberry Pi ή Synology NAS μέσω Docker.

# FD Alerts

Web εφαρμογή (Flask) για αποστολή SMS ειδοποιήσεων (Yuboto OMNI), επιλογή επαφών από λίστα, καταγραφή ποιος είδε το μήνυμα (landing page) και προβολή logs. Σχεδιασμένη για να τρέχει σε Docker (Synology ή Raspberry Pi) και να φορτώνει τα αρχεία της από GitHub repo.

---

## ✳️ Τι κάνει

- Αποστολή SMS σε έναν ή περισσότερους παραλήπτες
- Προδιαμορφωμένο μήνυμα “παίζουμε μπαλίτσα…” με ημερομηνία, ώρα, γήπεδο
- Αυτόματο link προς landing page για να πατάει ο παίκτης “Το είδα”
- Καταγραφή στο backend ποιος το είδε και πότε
- Σελίδα επαφών (contacts) που αποθηκεύεται σε JSON
- Δουλεύει με **Yuboto OMNI** (Basic auth)
- Σχεδιασμένο ώστε αργότερα να μπει και GSM module

---

## ⚙️ Μεταβλητές περιβάλλοντος

| Όνομα             | Περιγραφή                              | Παράδειγμα                         |
|-------------------|----------------------------------------|-------------------------------------|
| `PORT`            | Θύρα που θα ακούει το Flask            | `8899`                              |
| `SMS_PROVIDER`    | Πάροχος SMS                            | `omni`                              |
| `YUBOTO_API_KEY`  | API key της Yuboto (Basic)             | `MDBCNDZ...`                        |
| `SMS_SENDER`      | Όνομα αποστολέα                        | `FDTeam 2012`                       |
| `PUBLIC_BASE_URL` | URL που θα βάζει στο SMS για landing   | `https://alert.fdteam2012.gr`       |

> Αν δεν βάλεις `PUBLIC_BASE_URL`, θα βάλει τοπικό (`http://127.0.0.1:8899`) και η landing δεν θα ανοίγει απ’ έξω.

---

## 📁 Δομή

Μέσα στο container /app:

```text
/app
 ├── app.py
 ├── templates/
 │    ├── index.html
 │    ├── contacts.html
 │    └── landing.html
 ├── static/
 │    └── icons/logo_final.png
 ├── requirements.txt
 └── data/
      ├── contacts.json
      ├── logs.json
      └── views.json
Ο φάκελος data/ πρέπει να παραμένει επίμονος (volume) για να μη χάνονται επαφές και logs.

1️⃣ Εγκατάσταση μέσω Portainer από GitHub (πιο «καθαρή» μέθοδος)
Αυτό είναι το σενάριο: έχεις Synology ή Pi με Docker + Portainer και δεν θες να ανεβάζεις αρχεία με το χέρι. Το Portainer θα τραβήξει το repo και θα το τρέξει.

Μπες στο Portainer → Stacks → Add stack

Όνομα: fdalerts

Διάλεξε Repository

Βάλε:

Repository URL

text
Αντιγραφή κώδικα
https://github.com/maxsto73/fdalerts-app
Compose path

text
Αντιγραφή κώδικα
docker-compose.yml
Στο πεδίο environment (ή στο .env του stack) βάλε:

env
Αντιγραφή κώδικα
PORT=8899
SMS_PROVIDER=omni
YUBOTO_API_KEY=ΒΑΛΕ_ΤΟ_ΔΙΚΟ_ΣΟΥ
SMS_SENDER=FDTeam 2012
PUBLIC_BASE_URL=https://alert.fdteam2012.gr
Πάτα Deploy the stack

Άνοιξε στο browser:

text
Αντιγραφή κώδικα
http://IP_ΤΟΥ_SERVER:8899
Αν το repo ενημερωθεί, κάνεις Re-deploy το stack από το Portainer και θα ξανατραβήξει τον κώδικα.

2️⃣ Εγκατάσταση σε Synology Docker με Portainer αλλά με τοπικό φάκελο
Αυτό είναι το σενάριο που έχεις ήδη φάκελο στο NAS π.χ. /volume1/docker/fdalerts/app και θέλεις το container να τρέχει τον κώδικα από εκεί, αλλά στην εκκίνηση να κάνει και git pull αν υπάρχει repo.

Δημιούργησε φακέλους στο Synology:

bash
Αντιγραφή κώδικα
mkdir -p /volume1/docker/fdalerts/app
Μέσα στο Portainer → Stacks → Add stack και επικόλλησε αυτό:

yaml
Αντιγραφή κώδικα
version: "3.9"

services:
  fdalerts:
    image: python:3.11-slim
    container_name: fdalerts
    working_dir: /app
    ports:
      - "8899:8899"
    environment:
      PORT: 8899
      SMS_PROVIDER: omni
      YUBOTO_API_KEY: ΒΑΛΕ_ΤΟ_ΔΙΚΟ_ΣΟΥ
      SMS_SENDER: FDTeam 2012
      PUBLIC_BASE_URL: "https://alert.fdteam2012.gr"
    volumes:
      # εδώ ο κώδικας από το NAS
      - /volume1/docker/fdalerts/app:/app
    command: >
      sh -c "
        apt-get update && apt-get install -y git &&
        git config --global --add safe.directory /app &&
        if [ ! -d .git ]; then
          git clone https://github.com/maxsto73/fdalerts-app .;
        else
          git pull;
        fi &&
        pip install --no-cache-dir -r requirements.txt &&
        python app.py
      "
    restart: unless-stopped
Deploy

Αυτό που κάνει το command:

εγκαθιστά git

δηλώνει ότι το /app είναι “safe”

αν δεν υπάρχει repo → κάνει git clone

αν υπάρχει → κάνει git pull

εγκαθιστά dependencies

τρέχει Flask

Μετά το deploy:

text
Αντιγραφή κώδικα
http://IP_ΤΟΥ_NAS:8899
3️⃣ Εγκατάσταση με docker CLI (π.χ. σε Raspberry Pi χωρίς Portainer)
Αν είσαι κατευθείαν σε SSH:

bash
Αντιγραφή κώδικα
mkdir -p ~/fdalerts
cd ~/fdalerts
curl -O https://raw.githubusercontent.com/maxsto73/fdalerts-app/main/docker-compose.yml
Μετά άνοιξε το docker-compose.yml και βάλε τα δικά σου env (API key, base url κλπ).

Και τρέξε:

bash
Αντιγραφή κώδικα
docker compose up -d
ή αν έχεις το παλιό:

bash
Αντιγραφή κώδικα
docker-compose up -d
Και μετά:

text
Αντιγραφή κώδικα
http://IP_ΤΟΥ_PI:8899
🔁 Ενημέρωση / redeploy
Αν τρέχει από repo (όπως τα παραπάνω):

Μπαίνεις στο Portainer

Ανοίγεις το stack

Πατάς Update ή Re-deploy

Το container στην εκκίνηση ξανατρέχει το git pull (όπως το γράψαμε στο command), άρα παίρνει τον τελευταίο κώδικα.

Αν τρέχεις από τοπικό φάκελο:

αλλάζεις το αρχείο στο NAS (/volume1/docker/fdalerts/app/app.py)

και κάνεις Restart container από Portainer

🧪 Έλεγχος ότι όλα είναι ΟΚ
http://IP:8899 ανοίγει το web interface

στέλνεις SMS → πρέπει να γράψει log στο /app/data/logs.json

ανοίγεις το link από το SMS → πρέπει να χτυπήσει /r?id=... και να γραφτεί στο /app/data/views.json

στο UI πρέπει να βλέπεις ποιος πάτησε “Το είδα”

🛠 Συχνά θέματα
1. Landing ανοίγει σε 127.0.0.1
Βάλε σωστό PUBLIC_BASE_URL στο compose.

2. Δεν βρίσκει favicon
Βεβαιώσου ότι υπάρχει στο container:
/app/static/icons/logo_final.png
και στο template το path είναι /static/icons/logo_final.png

3. “destination path '.' already exists” στα logs
Σημαίνει ότι το container έκανε ήδη clone. Το έχουμε καλύψει με git pull στο command.

📦 Μελλοντικά
Προσθήκη επιλογής “GSM / Local SIM” με SIM800C

Export / import επαφών

Authentication στο web UI

Καλή μπάλα ⚽
