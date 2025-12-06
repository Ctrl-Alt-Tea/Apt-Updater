#!/bin/python3

import subprocess
import os, sys

PURPLE = '\033[95m'
CYAN = '\033[96m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
UNDERLINE = '\033[4m'
ORANGE = '\033[33m'
GREY = '\033[90m'
RESET = '\033[0;0m'  # Reset terminal color scheme

def run_update(command):
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in process.stdout:
            print(line, end='')  # Print each line as it is received
        process.wait()  # Wait for the process to complete
        if process.returncode != 0:
            print(f"An error occurred: {process.stderr.read()}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def display_menu():
    print("Select an Apt option below to update your system:")
    print(f'{GREEN}1. Update packages and sources')
    print("2. Upgrade packages")
    print("3. Remove uneeded dependancies")
    print(f'{GREY}4. Exit{RESET}')
    print(f'{ORANGE}5. Exit and clear terminal{RESET}')

def get_scan_options(choice):
    if choice == 1:
        return ['sudo', 'apt', 'update', '-y']
    elif choice == 2:
        return ['sudo', 'apt', 'upgrade', '-y']
    elif choice == 3:
        return ['sudo', 'apt', 'autoremove', '-y']
    elif choice == 4:
        print("Exiting...")
        exit()
    elif choice == 5:
        os.system('clear')   # Clear terminal
        sys.exit()
    else:
        print("Invalid choice. Please try again.")
        return None

def main():
    while True:
        url = "https://github.com/Ctrl-Alt-Tea"  # Github Link
        print(" ")
        print(f'{YELLOW}Apt Updater CLI UI by Dylan Rose{RESET}')
        print(f"\033]8;;{url}\a{BLUE}Find me on Github{RESET}\033]8;;\a")
        print(" ")
        display_menu()
        try:
            print(" ")
            choice = int(input("Enter your choice (1-5): "))
            command = get_scan_options(choice)
            if command:
                output = run_update(command)
                print(output)
        except ValueError:
            print("Please enter a valid number from the options presented above.")

if __name__ == "__main__":
    main()
