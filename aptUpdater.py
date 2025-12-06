#!/usr/bin/env python3

import subprocess
import os
import sys

# ──────────────────────────────────────────────
# Color Definitions
# ──────────────────────────────────────────────
COLORS = {
    "PURPLE": "\033[95m",
    "CYAN": "\033[96m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "ORANGE": "\033[33m",
    "GREY": "\033[90m",
    "RESET": "\033[0m",
}

# ──────────────────────────────────────────────
# Run apt command and stream output live
# ──────────────────────────────────────────────
def run_update(command: list[str]):
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        for line in process.stdout:
            print(line, end="")

        process.wait()
        if process.returncode != 0:
            print(f"{COLORS['ORANGE']}Error:{COLORS['RESET']} {process.stderr.read()}")

        return process.returncode

    except Exception as e:
        print(f"{COLORS['ORANGE']}Unexpected error:{COLORS['RESET']} {e}")
        return 1

# ──────────────────────────────────────────────
# Menu UI
# ──────────────────────────────────────────────
def display_menu():
    print("Select an APT option below:")
    print(f"{COLORS['GREEN']}1. Update package lists")
    print("2. Upgrade installed packages")
    print("3. Remove unused dependencies")
    print(f"{COLORS['GREY']}4. Exit")
    print(f"{COLORS['ORANGE']}5. Exit and clear terminal{COLORS['RESET']}")

def get_scan_options(choice: int):
    return {
        1: ["sudo", "apt", "update", "-y"],
        2: ["sudo", "apt", "upgrade", "-y"],
        3: ["sudo", "apt", "autoremove", "-y"],
        4: None,
        5: None,
    }.get(choice)

# ──────────────────────────────────────────────
# Main loop
# ──────────────────────────────────────────────
def main():
    url = "https://github.com/Ctrl-Alt-Tea"

    while True:
        print(f"\n{COLORS['YELLOW']}Apt Updater CLI UI by Dylan Rose{COLORS['RESET']}")
        print(f"\033]8;;{url}\a{COLORS['BLUE']}Find me on GitHub{COLORS['RESET']}\033]8;;\a\n")

        display_menu()

        try:
            choice = int(input("Enter choice (1–5): "))
            if choice == 4:
                print("Goodbye...")
                sys.exit()

            if choice == 5:
                os.system("clear")
                sys.exit()

            command = get_scan_options(choice)
            if command:
                run_update(command)
            else:
                print("Invalid option selected.")

        except ValueError:
            print("Enter a number between 1–5")

# ──────────────────────────────────────────────
if __name__ == "__main__":
    main()
