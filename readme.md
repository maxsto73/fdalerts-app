# 🚀 FD Alerts — Raspberry Pi Automation Installer

Το **FD Alerts** είναι ένα πλήρες εργαλείο διαχείρισης που εγκαθιστά και συντηρεί
την εφαρμογή *RasPiPush Ultimate* (FD Alerts Flask Service).  
Σχεδιασμένο για **Raspberry Pi / Debian / Synology**, προσφέρει πλήρως αυτοματοποιημένη
εγκατάσταση, ενημέρωση και δημιουργία αντιγράφων ασφαλείας.

---

## 🧩 Περιεχόμενα
- [⚙️ Χαρακτηριστικά](#️-χαρακτηριστικά)
- [📦 Εγκατάσταση](#-εγκατάσταση)
- [🧹 Απεγκατάσταση](#-απεγκατάσταση)
- [🛠️ Ενημέρωση / Επιδιόρθωση](#️-ενημέρωση--επιδιόρθωση)
- [💾 Backup & Restore](#-backup--restore)
- [🗂️ Ιστορικό Backups](#️-ιστορικό-backups)
- [🧠 Ελάχιστες Απαιτήσεις](#-ελάχιστες-απαιτήσεις)
- [📜 Credits](#-credits)

---

## ⚙️ Χαρακτηριστικά

✅ Πλήρης **αυτόματη εγκατάσταση** (Flask + systemd + virtualenv)  
✅ **Απεγκατάσταση** με πλήρη καθαρισμό υπηρεσιών και αρχείων  
✅ **Ενημέρωση** χωρίς απώλεια ρυθμίσεων (`config.json` / `messages.json`)  
✅ **Logs viewer** – Προβολή τελευταίων καταγραφών  
✅ **Restart & Status** με 1 επιλογή  
✅ **Backup / Restore** για πλήρη ασφάλεια ρυθμίσεων  
✅ **Ιστορικό Backups** με ημερομηνία, μέγεθος & αριθμό αρχείων  
✅ Φιλικό UI στη γραμμή εντολών, με ελληνικά & progress animation ✨

---

## 📦 Εγκατάσταση

Εκτέλεσε απλώς την παρακάτω εντολή στο Raspberry Pi ή Synology:

```bash
curl -sSL https://raw.githubusercontent.com/maxsto73/fdalerts-app/main/setup_fdalerts.txt | sudo bash

=======================================
 🚀 FD Alerts Management Utility
---------------------------------------
 1) Εγκατάσταση (Clean Install)
 2) Απεγκατάσταση
 3) Ενημέρωση / Επιδιόρθωση
 4) Προβολή Logs
 5) Επανεκκίνηση Υπηρεσίας
 6) Έλεγχος Κατάστασης
 7) Backup / Restore Config
 8) Προβολή Ιστορικού Backups
=======================================

Μετά την εγκατάσταση:

Άνοιξε το web interface στο browser σου:

👉 http://[IP_του_Raspberry]:8899

🧹 Απεγκατάσταση

Από το ίδιο μενού επίλεξε 2) Απεγκατάσταση.

Αφαιρεί:

Τον φάκελο /opt/raspipush_ultimate

Το systemd service fdalerts.service

🛠️ Ενημέρωση / Επιδιόρθωση

Απλώς επίλεξε 3) και το script θα:

Κατεβάσει την τελευταία έκδοση του repo

Διατηρήσει config.json και messages.json

Επανεκκινήσει την υπηρεσία αυτόματα

💾 Backup & Restore

Μέσω της επιλογής 7):

Δημιουργεί backup των config.json & messages.json με timestamp
(π.χ. /opt/backups_fdalerts/config_20251031_192300.json)

Μπορείς να επαναφέρεις οποιοδήποτε προηγούμενο αρχείο εύκολα

🗂️ Ιστορικό Backups

Η επιλογή 8) προβάλλει λίστα όλων των αποθηκευμένων backups με:

Ημερομηνία δημιουργίας

Μέγεθος αρχείου

Συνολικό πλήθος

Διαδρομή αποθήκευσης (/opt/backups_fdalerts)

🧠 Ελάχιστες Απαιτήσεις

Raspberry Pi OS / Debian / Ubuntu / Synology (με systemd)

Python 3.8+

Ενεργό internet connection

sudo δικαιώματα

📜 Credits

Ανάπτυξη: FDTeam 2012

Σχεδίαση script & αυτοματισμού: @maxsto73

Web API Integration: Yuboto SMS API

Υποστηριζόμενο Project: RasPiPush Ultimate

💡 Συνοψίζοντας

Το εργαλείο αυτό καθιστά τη διαχείριση του FD Alerts εντελώς αυτοματοποιημένη:

Από εγκατάσταση μέχρι backup, όλα γίνονται με ένα μόνο script!
------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------
---

## 💻 Οδηγίες για Developers (Mac & Raspberry)

Η ενότητα αυτή περιγράφει πώς μπορείς να τρέξεις, ενημερώσεις ή ανεβάσεις
την εφαρμογή **FD Alerts** τόσο από Raspberry όσο και από MacOS.

---

### 🧩 Εκτέλεση στο Raspberry Pi

Για πλήρη εγκατάσταση ή ενημέρωση, εκτέλεσε την παρακάτω εντολή:

```bash
curl -sSL https://raw.githubusercontent.com/maxsto73/fdalerts-app/main/setup_fdalerts.txt | sudo bash
💡 Αν θέλεις να το αποθηκεύσεις πρώτα και να το τρέξεις χειροκίνητα:

bash
Αντιγραφή κώδικα
curl -sSL https://raw.githubusercontent.com/maxsto73/fdalerts-app/main/setup_fdalerts.txt -o setup_fdalerts.txt
chmod +x setup_fdalerts.txt
sudo bash setup_fdalerts.txt
Μετά την εγκατάσταση, η εφαρμογή θα είναι διαθέσιμη στο browser:

👉 http://[IP του Raspberry]:8899

🧠 Κατέβασμα ολόκληρου του Repo (π.χ. σε νέο Pi)
Αν θέλεις να εγκαταστήσεις από καθαρό περιβάλλον:

bash
Αντιγραφή κώδικα
cd /opt
sudo apt install -y unzip
wget https://github.com/maxsto73/fdalerts-app/archive/refs/heads/main.zip -O fdalerts.zip
sudo unzip fdalerts.zip -d /opt
sudo mv /opt/fdalerts-app-main /opt/raspipush_ultimate
🧰 Ενημέρωση ή Ανέβασμα Αρχείων στο GitHub (MacOS)
Αν έχεις αλλάξει αρχεία (π.χ. app.py, setup_fdalerts.txt, templates/, κ.λπ.)
και θέλεις να ενημερώσεις το repo σου:

bash
Αντιγραφή κώδικα
cd ~/Desktop/raspipush_ultimate
git init
git branch -M main
git remote remove origin 2>/dev/null
git remote add origin https://github.com/maxsto73/fdalerts-app.git
git pull origin main --allow-unrelated-histories
git add .
git commit -m "Ενημέρωση αρχείων FD Alerts"
git push -u origin main
💡 Σημείωση: Αν σου ζητήσει password, βάλε το προσωπικό σου GitHub Personal Access Token (PAT),
όχι τον κωδικό σου.

🔁 Ενημέρωση μόνο (χωρίς νέα σύνδεση)
Αν έχεις ήδη συνδεδεμένο το repo (git remote -v δείχνει το origin):

bash
Αντιγραφή κώδικα
cd ~/Desktop/raspipush_ultimate
git add .
git commit -m "Update app & installer"
git push
📜 Σύνοψη Εντολών
Ενέργεια	Εντολή
Εγκατάσταση στο Pi	curl -sSL https://raw.githubusercontent.com/maxsto73/fdalerts-app/main/setup_fdalerts.txt | sudo bash
Τοπική εκτέλεση setup	curl -sSL … -o setup_fdalerts.txt && chmod +x setup_fdalerts.txt && sudo bash setup_fdalerts.txt
Upload από Mac στο GitHub	git add . && git commit -m "update" && git push
Κατέβασμα repo σε νέο Pi	wget https://github.com/maxsto73/fdalerts-app/archive/refs/heads/main.zip

🔧 Tip: Μπορείς να κρατήσεις ένα backup του setup script και στο Synology σου,
ώστε αν ποτέ “πέσει” το GitHub, να μπορείς να τρέξεις:

bash
Αντιγραφή κώδικα
curl -sSL https://www.fdteam2012.gr/raspush/setup_fdalerts.txt | sudo bash
📦 Τελευταία ενημέρωση: Νοέμβριος 2025
👨‍💻 Συντήρηση: FDTeam 2012 / @maxsto73
