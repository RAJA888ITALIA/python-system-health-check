# Strumento per il monitoraggio del sistema IT e il triage dei log

Uno strumento CLI in Python che automatizza le attività quotidiane di diagnostica IT: controlli dello stato del sistema locale (CPU, RAM e disco), verifiche della raggiungibilità degli host remoti e analisi dei file di log, il tutto raccolto in un unico report degli incidenti.

[English](README.md) | **Italiano**

## Funzionalità

* **Controllo dello stato del sistema** — monitora l'utilizzo di CPU, RAM e disco confrontandolo con soglie configurabili (utilizzando `psutil` e `shutil`).
* **Triage dei log** — analizza un file di log alla ricerca di messaggi `ERROR` / `WARNING` utilizzando regex con confini di parola, evitando corrispondenze all'interno di parole non correlate come `TERROR`.
* **Raggiungibilità della rete** — esegue controlli ping multipiattaforma (Windows/Linux) tramite `subprocess`.
* **Generazione dei report** — crea un file `report.txt` formattato con un riepilogo dei risultati, insieme a un sistema di logging strutturato sulla console.
* **Configurabile da CLI** — tutte le principali impostazioni sono configurabili tramite opzioni da riga di comando, permettendo di eseguire lo strumento autonomamente, all'interno di script o secondo una pianificazione (ad esempio tramite cron).
* **Resiliente** — le operazioni di sistema sono gestite tramite meccanismi di error handling, fornendo messaggi di errore chiari invece di causare il crash del programma.

## Installazione

```bash
pip install -r requirements.txt
```

## Utilizzo

Esegui lo strumento con le impostazioni predefinite (nessun file di log, verifica `8.8.8.8` e l'indirizzo di test `192.0.2.254` e genera `report.txt`):

```bash
python health_tool.py
```

Esegui lo strumento con opzioni personalizzate:

```bash
python health_tool.py \
  --log /var/log/syslog \
  --output incident_report.txt \
  --servers 8.8.8.8 1.1.1.1 \
  --cpu-threshold 80 \
  --ram-threshold 85 \
  --disk-threshold 85
```

Per visualizzare le istruzioni aggiuntive e tutte le opzioni disponibili:

```bash
python health_tool.py --help
```

### Opzioni CLI

| Opzione            | Descrizione                                                                         | Valore predefinito                        |
| ------------------ | ----------------------------------------------------------------------------------- | ----------------------------------------- |
| `--log`, `-l`      | Percorso del file di log da analizzare per individuare messaggi `ERROR` / `WARNING` | Nessuno (l'analisi dei log viene saltata) |
| `--output`, `-o`   | Percorso in cui salvare il report                                                   | `report.txt`                              |
| `--servers`, `-s`  | Uno o più host/indirizzi IP da verificare tramite ping                              | `8.8.8.8 192.0.2.254`                     |
| `--disk-threshold` | Percentuale di utilizzo del disco oltre la quale viene generato un avviso           | `85.0`                                    |
| `--cpu-threshold`  | Percentuale di utilizzo della CPU oltre la quale viene generato un avviso           | `80.0`                                    |
| `--ram-threshold`  | Percentuale di utilizzo della RAM oltre la quale viene generato un avviso           | `85.0`                                    |

## Esempio di output

```text
=========================================
     MASTER IT INCIDENT & SYSTEM REPORT
=========================================

--- STORAGE HEALTH ---
OK: Disk capacity is healthy (42.10%)

--- CPU & MEMORY HEALTH ---
OK: CPU and RAM usage are healthy
CPU: 12.30%
RAM: 51.20%

--- NETWORK STATUS ---
REACHABLE: 8.8.8.8
FAILED: 192.0.2.254 (UNREACHABLE)

--- LOG TRIAGE SUMMARY ---
3 ERRORS AND 1 WARNINGS HAVE BEEN FOUND
--- DETAILED ERROR LOGS ---
...
```

> Nota: l'output del programma rimane in inglese, poiché i messaggi mostrati sopra corrispondono all'output effettivo della CLI.

## Possibili miglioramenti futuri

* Aggiungere un'opzione per esportare i risultati in formato JSON (`--json`) oltre al report testuale, facilitando l'integrazione con dashboard e altri strumenti.
* Aggiungere notifiche tramite email o Slack quando vengono superate le soglie configurate.
* Aggiungere test con `unittest.mock` per simulare diverse condizioni del sistema senza interagire direttamente con il sistema reale.
