# == SYSTEM HEALTH CHECK SCRIPT == #
import logging
import os
import platform
import subprocess
import shutil
import psutil
import re
import argparse

#for logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s"
)
#ALL_FUNCTIONS_
class SystemMonitor:
    def __init__(
        self,
        disk_threshold: float=85.0,
        cpu_threshold: float=80.0,
        ram_threshold: float=85.0
    ):
        self.disk_threshold = disk_threshold
        self.cpu_threshold = cpu_threshold
        self.ram_threshold = ram_threshold

    #1
    @staticmethod
    def analyze_log(log_file_path):
        if not log_file_path:
            logging.info("Log analysis skipped or file not found.")
            return 0, 0, ["[!] LOG ANALYSIS SKIPPED BY USER\n"]

        error_count = 0
        warning_count = 0
        err_pattern = re.compile(r"\bERROR\b", re.IGNORECASE)
        warn_pattern = re.compile(r"\bWARNING\b", re.IGNORECASE)
        report = []
        logging.info(f"Scanning log file: {log_file_path}")
        try:
            with open(log_file_path, "r", encoding="utf-8") as log_file:
                for line in log_file:
                    if err_pattern.search(line):
                        logging.warning(f"Error entry found: {line.strip()}")  # line.strip(): removes extra newline break
                        error_count += 1
                        report.append(line)
                    elif warn_pattern.search(line):
                        logging.info(f"Warning entry found: {line.strip()}")
                        warning_count += 1
                        report.append(line)
        except FileNotFoundError as e:
            logging.error(f"Failed to parse log file: {e}")
            report.append(f"[!] ERROR: File '{log_file_path}' could not be read.\n")
        except (PermissionError, UnicodeDecodeError, OSError) as e:
            logging.error(f"Unexpected error while reading log file: {e}")
            report.append(f"[!] ERROR: Could not fully process '{log_file_path}' {e}\n")
        return error_count, warning_count, report

    #2
    def check_storage(self):
        try:
            target_path = "C:\\" if platform.system().lower() == "windows" else "/"
            total, used, free = shutil.disk_usage(target_path)
            percent_used=(used/total)*100
            free_gb = free / (1024 ** 3)

            logging.info(f"Storage check: {percent_used:.2f}% used, {free_gb:.2f}GB free.")

            if percent_used > self.disk_threshold:
                return f"WARNING: Disk capacity is running out! \nUsed: {percent_used:.2f}%"
            else:
                return f"OK: Disk capacity is healthy ({percent_used:.2f}%)"
        except OSError as e:
            logging.error(f"Storage check failed: {e}")
            return f"ERROR: Could not determine disk usage: {e}"

    #3
    def check_metrics(self):
        try:
            #for CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            #for ram metrics
            ram_usage = psutil.virtual_memory().percent
            #GB=bytes/1024^3
            alerts=[]
            if cpu_usage > self.cpu_threshold:
                alerts.append(f"WARNING: HIGH CPU LOAD DETECTED: {cpu_usage:.2f}%")
            if ram_usage > self.ram_threshold:
                alerts.append(f"WARNING: HIGH MEMORY LOAD DETECTED: {ram_usage:.2f}% ")

            if alerts:  #== True
                return "\n".join(alerts)
            return f"OK: CPU and RAM usage are healthy\nCPU: {cpu_usage:.2f}%\nRAM: {ram_usage:.2f}%"
        except psutil.Error as e:
            logging.error(f"CPU/RAM check failed: {e}")
            return f"ERROR: Could not determine CPU/RAM usage: {e}"

    #4
    @staticmethod
    def check_network(target_servers):
        is_windows = platform.system().lower() == "windows"
        count_param = "-n" if is_windows else "-c"
        timeout_param = ["-w", "1000"] if is_windows else ["-W", "1"] #-w: saves time

        network_result = []
        for server in target_servers:
            command = ["ping", count_param, "1"] + timeout_param + [server]
            try:
                response = subprocess.run(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell = False
                )
                if response.returncode == 0:
                    status = f"REACHABLE: {server}"
                else:
                    status = f"FAILED: {server} (UNREACHABLE)"
            except (FileNotFoundError, OSError) as e:
                logging.error(f"Ping command failed for: {server}: {e}")
                status = f"ERROR: {server} (could not run ping {e})"
            logging.info(f"Network status for {server}: {status}")
            network_result.append(status)
        return network_result
    #5
    @staticmethod
    def generate_report (output_file, disk, cpu_ram, network, error_count, warning_count, report):
        try:
            with open(output_file, "w", encoding="utf-8") as report_file:
                report_file.write("=========================================\n")
                report_file.write("     MASTER IT INCIDENT & SYSTEM REPORT   \n")
                report_file.write("=========================================\n\n")

                report_file.write("--- STORAGE HEALTH ---\n")
                report_file.write(f"{disk}\n\n")

                report_file.write("--- CPU & MEMORY HEALTH ---\n")
                report_file.write(f"{cpu_ram}\n\n")

                report_file.write("--- NETWORK STATUS ---\n")
                for net in network:
                    report_file.write(f"{net}\n")
                report_file.write("\n")

                report_file.write("--- LOG TRIAGE SUMMARY ---\n")
                report_file.write(f"{error_count} ERRORS AND {warning_count} WARNINGS HAVE BEEN FOUND\n")
                report_file.write("--- DETAILED ERROR LOGS ---\n")
                for line in report:
                    report_file.write(line)
            logging.info(f"Master report file '{output_file}' generated successfully.")
        except OSError as e:
            logging.error(f"Failed to write report file: '{output_file}' {e}")
            print(f"[!] ERROR: Could not write report to '{output_file}': {e}")


#ARG
def parse_arg():
    parser = argparse.ArgumentParser(
        description="IT System Health Tool & Log Triage Tool"
    )
    parser.add_argument(
        "--output", "-o",
        dest="output_file",
        default="report.txt",
        help="Path to write the generated report to (default: report.txt)",
    )
    parser.add_argument(
        "--log-file", "-l",
        dest="log_file",
        default=None,
        help="Path to an input log file to parse for errors/warnings"
    )
    parser.add_argument(
        "--servers", "-s",
        dest="target_servers", #servers
        nargs="+",
        default=["8.8.8.8", "192.0.2.254"],
        help="One or more hostnames/IPs to ping for reachability (default: all 8.8.8.8 192.0.2.254)"
    )
    parser.add_argument(
        "--disk-threshold",
        type=float,
        default=85.0,
        help="Disk usage percent that triggers a WARNING (default: 85.0)."
    )
    parser.add_argument(
        "--cpu-threshold",
        type=float,
        default=80.0,
        help="CPU usage percent that triggers a WARNING (default: 80.0)."
    )
    parser.add_argument(
        "--ram-threshold",
        type=float,
        default=85.0,
        help="RAM usage percent that triggers a WARNING (default: 85.0)."
    )
    return parser.parse_args()

#-- MAIN --#
def main():
    args = parse_arg()
    monitor = SystemMonitor(
        disk_threshold=args.disk_threshold,
        cpu_threshold=args.cpu_threshold,
        ram_threshold=args.ram_threshold
    )
    log_file_path = args.log_file

    if log_file_path and not os.path.exists(log_file_path):
        print(f"[!] Log file: '{log_file_path}' does not exist. Skipping log analysis.")
        logging.error(f"Provided log path does not exist: {log_file_path}")
        log_file_path = None

    output_file = args.output_file
    test_servers = args.target_servers  #= 1 valid IP (Google DNS) & 1 fake IP
    err, war, report = monitor.analyze_log(log_file_path)
    disk_status = monitor.check_storage()
    cpu_ram_status = monitor.check_metrics()
    network_result = monitor.check_network(test_servers)
    monitor.generate_report(output_file, disk_status, cpu_ram_status, network_result, err, war, report)

#RUNNING MAIN PROGRAM
if __name__ == "__main__":
    main()