#!/usr/bin/env python3

import subprocess
import os
import sys
import re
import logging
from datetime import datetime

# ──────────────────────────────────────────────
# Constants & Configuration
# ──────────────────────────────────────────────
GITHUB_URL = "https://github.com/Ctrl-Alt-Tea"
# Use a hidden log file in the user's home directory
LOG_DIR = os.path.expanduser("~/.local/share/Apt-Updater")
LOG_FILE = os.path.join(LOG_DIR, "apt-updater.log")

COLORS = {
    "PURPLE": "\033[95m",
    "CYAN": "\033[96m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "ORANGE": "\033[33m",
    "RED": "\033[91m",
    "GREY": "\033[90m",
    "RESET": "\033[0m",
}

# ──────────────────────────────────────────────
# Logging Setup
# ──────────────────────────────────────────────
def setup_logging():
    # Ensure the log directory exists
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except Exception:
        # If we can't create the directory, fall back to the current directory
        global LOG_FILE
        LOG_FILE = "apt-updater.log"

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def log_action(message):
    logging.info(message)

# ──────────────────────────────────────────────
# UI Components
# ──────────────────────────────────────────────
class UI:
    @staticmethod
    def print_banner():
        print(f"\033]8;;{GITHUB_URL}\a{COLORS['BLUE']}Follow this dev on GitHub{COLORS['RESET']}\033]8;;\a")

    @staticmethod
    def print_header(text, color="YELLOW"):
        print(f"\n{COLORS[color]}### {text} ###{COLORS['RESET']}")

    @staticmethod
    def print_error(text):
        print(f"{COLORS['RED']}Error: {text}{COLORS['RESET']}")

    @staticmethod
    def print_success(text):
        print(f"{COLORS['GREEN']}{text}{COLORS['RESET']}")

    @staticmethod
    def draw_progress_bar(percent, message=""):
        bar_length = 30
        filled_length = int(bar_length * percent // 100)
        bar = "█" * filled_length + "-" * (bar_length - filled_length)
        sys.stdout.write(f"\r{COLORS['CYAN']}[{bar}] {percent:.1f}%{COLORS['RESET']} - {message} \033[K")
        sys.stdout.flush()

    @staticmethod
    def print_summary(updated_packages: set[str], command_name: str):
        if not updated_packages:
            print(f"\n{COLORS['YELLOW']}No packages were installed, upgraded, or removed.{COLORS['RESET']}")
            return

        print(f"\n{COLORS['GREEN']}✅ {command_name} Summary ({len(updated_packages)} Packages){COLORS['RESET']}")
        print("-" * 40)

        package_list = sorted(list(updated_packages))
        num_cols = 2
        items_per_col = (len(package_list) + num_cols - 1) // num_cols

        for i in range(items_per_col):
            line = ""
            for j in range(num_cols):
                index = i + j * items_per_col
                if index < len(package_list):
                    package = package_list[index]
                    line += f"{COLORS['PURPLE']}{package:<20}{COLORS['RESET']}"
                else:
                    line += " " * 20
            print(line)
        print("-" * 40)
        sys.stdout.flush()

# ──────────────────────────────────────────────
# System Information
# ──────────────────────────────────────────────
class SystemInfo:
    @staticmethod
    def get_output(command: list[str]) -> str:
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=5)
            return result.stdout.strip()
        except Exception:
            return "N/A"

    @classmethod
    def display(cls):
        UI.print_header("System Information")

        os_info = cls.get_output(["hostnamectl"])
        os_line = "N/A"
        hostname = "N/A"
        for line in os_info.splitlines():
            if "Static hostname:" in line:
                hostname = line.split(':')[-1].strip()
            if "Operating System:" in line:
                os_line = line.split(':')[-1].strip()

        print(f"{COLORS['CYAN']}Hostname:         {COLORS['RESET']}{hostname}")
        print(f"{COLORS['CYAN']}Operating System: {COLORS['RESET']}{os_line}")
        print(f"{COLORS['CYAN']}Kernel Version:   {COLORS['RESET']}{cls.get_output(['uname', '-r'])}")
        print(f"{COLORS['CYAN']}Last Boot:        {COLORS['RESET']}{cls.get_output(['uptime', '-s'])}")

        df_output = cls.get_output(["df", "-h", "/"])
        used_percent = "N/A"
        if df_output != "N/A":
            lines = df_output.splitlines()
            if len(lines) > 1:
                parts = lines[-1].split()
                used_percent = parts[4] if len(parts) > 4 else "N/A"
        print(f"{COLORS['CYAN']}Root Disk Used:   {COLORS['RESET']}{used_percent}")
        print(f"{COLORS['YELLOW']}##########################{COLORS['RESET']}\n")

# ──────────────────────────────────────────────
# APT Manager
# ──────────────────────────────────────────────
class AptManager:
    PACKAGE_RE = re.compile(r'^(?:Inst|Upgrading|Unpacking|Remv) ([\w\d\-\+\.]+)(?: |:|\().*')

    @staticmethod
    def check_root():
        if os.geteuid() != 0:
            # We check if sudo is available even if not root, because the script uses sudo in commands.
            # But it's better to be sure we can run sudo.
            try:
                subprocess.run(["sudo", "-n", "true"], check=True, capture_output=True)
            except Exception:
                UI.print_error("This script requires root privileges or passwordless sudo to function correctly for most options.")
                UI.print_error("Please run with sudo or as root.")
                # We don't exit here because search might work without sudo, but actually the commands have sudo prepended.

    def run_command(self, command: list[str], dry_run: bool = False, is_search: bool = False):
        updated_packages = set()
        command_name = command[2].capitalize() if len(command) > 2 else "Operation"
        
        log_action(f"Starting command: {' '.join(command)}")

        is_upgrading = not dry_run and command_name in ["Upgrade", "Dist-upgrade"]
        cmd_to_run = list(command)
        if is_upgrading:
            cmd_to_run += ["-o", "APT::Status-Fd=1"]
            print(f"{COLORS['GREY']}Initializing process...{COLORS['RESET']}")
        
        try:
            process = subprocess.Popen(
                cmd_to_run,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Capture stderr as well
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            current_percent = 0.0
            current_msg = "Starting..."

            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                if line:
                    stripped_line = line.strip()
                    
                    match = self.PACKAGE_RE.match(stripped_line)
                    if match:
                        updated_packages.add(match.group(1))

                    if is_upgrading:
                        is_status_line = False
                        if stripped_line.startswith(('dlstatus', 'pmstatus')):
                            is_status_line = True
                            parts = stripped_line.split(':')
                            if len(parts) >= 3:
                                try:
                                    current_percent = float(parts[1])
                                    current_msg = parts[2]
                                    UI.draw_progress_bar(current_percent, current_msg)
                                except ValueError:
                                    pass
                        elif stripped_line.startswith('media-change'):
                            is_status_line = True
                            sys.stdout.write("\r\033[K")
                            print(f"{COLORS['ORANGE']}Media change required: {stripped_line}{COLORS['RESET']}")
                            UI.draw_progress_bar(current_percent, current_msg)

                        if stripped_line and not is_status_line:
                            sys.stdout.write("\r\033[K")
                            print(stripped_line)
                            UI.draw_progress_bar(current_percent, current_msg)
                    elif stripped_line:
                        print(stripped_line)

            process.stdout.close()
            return_code = process.wait()

            if is_upgrading:
                UI.draw_progress_bar(100.0, "Complete")
                print()

            if return_code != 0:
                UI.print_error(f"Process finished with error code: {return_code}")
                log_action(f"Command failed with return code {return_code}")
            else:
                log_action(f"Command completed successfully. Packages affected: {len(updated_packages)}")
                if dry_run:
                    UI.print_success("\nDry run complete. No changes were made.")
                elif is_search:
                    UI.print_success("Search complete.")
                elif command_name in ["Upgrade", "Dist-upgrade", "Autoremove"]:
                    UI.print_summary(updated_packages, command_name)

            return return_code

        except KeyboardInterrupt:
            print(f"\n{COLORS['ORANGE']}Process cancelled by user.{COLORS['RESET']}")
            log_action("Process cancelled by user.")
            return 1
        except Exception as e:
            UI.print_error(f"Unexpected error: {e}")
            log_action(f"Unexpected error: {e}")
            return 1

# ──────────────────────────────────────────────
# Main Application
# ──────────────────────────────────────────────
class AptUpdaterApp:
    def __init__(self):
        self.apt_manager = AptManager()
        self.show_sysinfo = True

    def display_menu(self):
        print("Select an APT option below:")
        print(f"{COLORS['GREEN']}1. Update package lists")
        print("2. Upgrade installed packages")
        print("3. Distro/System Upgrade")
        print("4. Remove unused dependencies")
        print(f"{COLORS['YELLOW']}5. Preview upgrade (Dry Run)")
        print(f"{COLORS['CYAN']}6. Search for a package")
        print(f"{COLORS['PURPLE']}7. Toggle System Information (Currently: {'ON' if self.show_sysinfo else 'OFF'})")
        print(f"{COLORS['GREY']}8. Exit")
        print(f"{COLORS['ORANGE']}9. Exit and clear terminal{COLORS['RESET']}")

    def get_command(self, choice):
        return {
            1: ["sudo", "apt-get", "update", "-y"],
            2: ["sudo", "apt-get", "upgrade", "-y"],
            3: ["sudo", "apt-get", "dist-upgrade", "-y"],
            4: ["sudo", "apt-get", "autoremove", "-y"],
            5: ["sudo", "apt-get", "upgrade", "--dry-run"],
            6: ["sudo", "apt-cache", "search"],
        }.get(choice)

    def run(self):
        setup_logging()
        self.apt_manager.check_root()

        while True:
            UI.print_banner()
            if self.show_sysinfo:
                SystemInfo.display()
            
            self.display_menu()
            
            try:
                choice_input = input(f"Enter choice (1–9): ").strip()
                if not choice_input:
                    continue

                choice = int(choice_input)

                if choice == 7:
                    self.show_sysinfo = not self.show_sysinfo
                    continue
                if choice == 8:
                    print(f"\n{COLORS['YELLOW']}Goodbye and stay awesome ...{COLORS['RESET']}")
                    UI.print_banner()
                    break
                if choice == 9:
                    os.system("clear")
                    break

                command = self.get_command(choice)
                if command:
                    is_dry_run = (choice == 5)
                    is_search = (choice == 6)

                    if is_search:
                        search_term = input(f"{COLORS['CYAN']}Enter package name to search: {COLORS['RESET']}").strip()
                        if search_term:
                            command.append(search_term)
                        else:
                            UI.print_error("Search term cannot be empty.")
                            continue

                    self.apt_manager.run_command(command, dry_run=is_dry_run, is_search=is_search)
                else:
                    UI.print_error("Invalid option selected.")

            except ValueError:
                UI.print_error("Please enter a valid number (1-9).")
            except KeyboardInterrupt:
                print("\nGoodbye...")
                break

if __name__ == "__main__":
    app = AptUpdaterApp()
    app.run()
