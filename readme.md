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
