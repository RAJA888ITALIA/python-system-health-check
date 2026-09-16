# IT System Health & Log Triage Tool

A Python CLI tool that automates daily IT support diagnostics: local system health checks (CPU, RAM, disk), remote host reachability checks, and log file triage — all rolled into a single incident report.

[English](README.md) | [Italiano](README.it.md)

## Features

* **System health checks** — CPU, RAM, and disk usage against configurable thresholds (using `psutil` and `shutil`).
* **Log triage** — scans a log file for `ERROR` / `WARNING` entries using word-boundary regex, avoiding matches inside unrelated words such as `TERROR`.
* **Network reachability** — cross-platform (Windows/Linux) ping checks via `subprocess`.
* **Incident reporting** — generates a formatted `report.txt` summarizing the results, along with structured console logging.
* **CLI-driven** — fully configurable via command-line flags, so it can run standalone, in a script, or on a schedule (e.g. cron).
* **Resilient** — system operations are wrapped in error handling, providing clear error messages instead of crashes.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run with defaults (no log file, pings `8.8.8.8` and the test address `192.0.2.254`, and writes `report.txt`):

```bash
python health_tool.py
```

Run with custom options:

```bash
python health_tool.py \
  --log /var/log/syslog \
  --output incident_report.txt \
  --servers 8.8.8.8 1.1.1.1 \
  --cpu-threshold 80 \
  --ram-threshold 85 \
  --disk-threshold 85
```

For additional instructions and available options, run:

```bash
python health_tool.py --help
```

### CLI Options

| Flag               | Description                                                | Default                   |
| ------------------ | ---------------------------------------------------------- | ------------------------- |
| `--log`, `-l`      | Path to a log file to scan for `ERROR` / `WARNING` entries | None (skips log analysis) |
| `--output`, `-o`   | Path to write the report to                                | `report.txt`              |
| `--servers`, `-s`  | One or more hosts/IPs to ping                              | `8.8.8.8 192.0.2.254`     |
| `--disk-threshold` | Disk usage percentage that triggers a warning              | `85.0`                    |
| `--cpu-threshold`  | CPU usage percentage that triggers a warning               | `80.0`                    |
| `--ram-threshold`  | RAM usage percentage that triggers a warning               | `85.0`                    |

## Example Output

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

## Possible Future Improvements

* Add a JSON export option (`--json`) alongside the text report for easier ingestion by dashboards.
* Add email/Slack alerting when thresholds are breached.
* Add tests using `unittest.mock` to simulate system conditions without interacting with the real system.
