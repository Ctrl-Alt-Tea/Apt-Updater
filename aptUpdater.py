#!/usr/bin/env python3

import subprocess
import os
import sys
import re

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
# Helper: Draw Progress Bar
# ──────────────────────────────────────────────
def draw_progress_bar(percent, message=""):
    """Draws a progress bar to the terminal."""
    bar_length = 30
    filled_length = int(bar_length * percent // 100)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    sys.stdout.write(f"\r{COLORS['CYAN']}[{bar}] {percent:.1f}%{COLORS['RESET']} - {message} \033[K")
    sys.stdout.flush()

# ──────────────────────────────────────────────
# Helper: Print Summary
# ──────────────────────────────────────────────
def print_summary(updated_packages: set[str], command_name: str):
    """Prints a formatted summary of updated packages."""
    
    # Ensure updated_packages is not None before proceeding
    if updated_packages is None or not updated_packages:
        print(f"\n{COLORS['YELLOW']}No packages were installed, upgraded, or removed.{COLORS['RESET']}")
        sys.stdout.flush()
        return

    print(f"\n{COLORS['GREEN']}✅ {command_name} Summary ({len(updated_packages)} Packages){COLORS['RESET']}")
    print("-" * 40)
    
    num_cols = 2
    # Ensure we operate on a list for reliable indexing
    package_list = sorted(list(updated_packages)) 
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
# Run apt-get command and stream output 
# ──────────────────────────────────────────────
def run_update(command: list[str], dry_run: bool = False, is_search: bool = False):
    PACKAGE_RE = re.compile(r'^(?:Inst|Upgrading|Unpacking|Remv) ([\w\d\-\+\.]+)(?: |:|\().*')
    updated_packages = set()

    try:
        command_name = command[2].capitalize() if len(command) > 2 else "Operation"
        cmd_with_status = command
        
        is_upgrading = not dry_run and command_name in ["Upgrade", "Dist-upgrade"]
        if is_upgrading:
            # Only inject status-fd flag for complex upgrade operations
            cmd_with_status = command + ["-o", "APT::Status-Fd=1"]
            print(f"{COLORS['GREY']}Initializing process...{COLORS['RESET']}")
        
        process = subprocess.Popen(
            cmd_with_status, 
            stdout=subprocess.PIPE, 
            stderr=None, 
            text=True
        )

        current_percent = 0.0
        current_msg = "Starting..."

        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            
            if line:
                stripped_line = line.strip()
                
                # Capture package names
                match = PACKAGE_RE.match(stripped_line)
                if match:
                    updated_packages.add(match.group(1))

                # Handle progress bar output
                if is_upgrading:
                    
                    is_status_line = False
                    
                    if stripped_line.startswith(('dlstatus', 'pmstatus')):
                        is_status_line = True
                        parts = stripped_line.split(':')
                        if len(parts) >= 3:
                            try:
                                current_percent = float(parts[1])
                                current_msg = parts[2]
                                draw_progress_bar(current_percent, current_msg)
                            except ValueError:
                                pass
                    elif stripped_line.startswith('media-change'):
                        is_status_line = True
                        # Media change request logic...
                        sys.stdout.write("\r\033[K")
                        print(f"{COLORS['ORANGE']}Media change required: {stripped_line}{COLORS['RESET']}")
                        draw_progress_bar(current_percent, current_msg)
                    
                    # Normal Output: Only print lines that are NOT status lines
                    if stripped_line and not is_status_line:
                        sys.stdout.write("\r\033[K") # Clear the progress bar line
                        print(stripped_line)        # Print the normal output
                        draw_progress_bar(current_percent, current_msg) # Redraw bar below
                
                # If it's search, update, autoremove, or dry-run, just print the output normally
                elif stripped_line:
                    print(stripped_line)

        # --- Explicitly close the pipe ---
        process.stdout.close()


        # Final actions after process completes
        if is_upgrading:
            draw_progress_bar(100.0, "Complete")
            print() # Prints a newline
            sys.stdout.flush() # Force flush the progress bar output
        
        # Report Success/Failure and Run Summary
        if process.returncode != 0:
            print(f"\n{COLORS['ORANGE']}Process finished with error code: {process.returncode}{COLORS['RESET']}")
            sys.stdout.flush()
        else:
            if dry_run:
                print(f"\n{COLORS['GREEN']}Dry run complete. No changes were made.{COLORS['RESET']}")
                sys.stdout.flush()
            elif is_search:
                 print(f"{COLORS['GREEN']}Search complete.{COLORS['RESET']}")
                 sys.stdout.flush()
            # Only call print_summary if it's a non-dry-run, non-search operation
            elif command_name in ["Upgrade", "Dist-upgrade", "Autoremove"]:
                print_summary(updated_packages, command_name)
        
        # --- Return the ACTUAL process return code ---
        return process.returncode
        
    except KeyboardInterrupt:
        print(f"\n{COLORS['ORANGE']}Process cancelled by user.{COLORS['RESET']}")
        return 1
    except Exception as e:
        # Fallback for unexpected Python errors (not process errors)
        if 'process' in locals() and process.returncode is not None:
            return process.returncode
        
        print(f"\n{COLORS['ORANGE']}Unexpected error:{COLORS['RESET']} {e}")
        return 1

# ──────────────────────────────────────────────
# System Information (Displays automatically)
# ──────────────────────────────────────────────
def get_command_output(command: list[str]) -> str:
    """Safely runs a shell command and returns the output."""
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True,
            timeout=5
        )
        return result.stdout.strip()
    except Exception:
        return "N/A"

def display_system_info():
    print(f"\n{COLORS['YELLOW']}### System Information ###{COLORS['RESET']}")
    
    # 1. Hostname and OS
    os_info = get_command_output(["hostnamectl"])
    os_line = ""
    for line in os_info.splitlines():
        if "Static hostname:" in line:
            print(f"{COLORS['CYAN']}Hostname:         {COLORS['RESET']}{line.split(':')[-1].strip()}")
        if "Operating System:" in line:
            os_line = line.split(':')[-1].strip()
    print(f"{COLORS['CYAN']}Operating System: {COLORS['RESET']}{os_line}")
    
    # 2. Kernel
    kernel = get_command_output(["uname", "-r"])
    print(f"{COLORS['CYAN']}Kernel Version:   {COLORS['RESET']}{kernel}")
    
    # 3. Uptime/Last Boot
    uptime = get_command_output(["uptime", "-s"])
    print(f"{COLORS['CYAN']}Last Boot:        {COLORS['RESET']}{uptime}")
    
    # 4. Disk Space (Root Partition)
    df_output = get_command_output(["df", "-h", "/"])
    if df_output != "N/A":
        lines = df_output.splitlines()
        if len(lines) > 1:
            parts = df_output.splitlines()[-1].split()
            used_percent = parts[4] if len(parts) > 4 else "N/A"
            print(f"{COLORS['CYAN']}Root Disk Used:   {COLORS['RESET']}{used_percent}")

    print(f"{COLORS['YELLOW']}##########################{COLORS['RESET']}")
    print(" ")


# ──────────────────────────────────────────────
# Menu UI
# ──────────────────────────────────────────────
def display_menu():
    print("Select an APT option below:")
    print(f"{COLORS['GREEN']}1. Update package lists")
    print("2. Upgrade installed packages")
    print("3. Distro/System Upgrade")
    print("4. Remove unused dependencies")
    print(f"{COLORS['YELLOW']}5. Preview upgrade (Dry Run)")
    print(f"{COLORS['CYAN']}6. Search for a package (apt-cache search)")
    print(f"{COLORS['GREY']}7. Exit")
    print(f"{COLORS['ORANGE']}8. Exit and clear terminal{COLORS['RESET']}")


def get_scan_options(choice: int):
    return {
        1: ["sudo", "apt-get", "update", "-y"],
        2: ["sudo", "apt-get", "upgrade", "-y"],
        3: ["sudo", "apt-get", "dist-upgrade", "-y"], #Dist upgrade
        4: ["sudo", "apt-get", "autoremove", "-y"],
        5: ["sudo", "apt-get", "upgrade", "--dry-run"],
        6: ["sudo", "apt-cache", "search"],
        7: None,
        8: None,
    }.get(choice)

# ──────────────────────────────────────────────
# Main loop
# ──────────────────────────────────────────────
def main():
    url = "https://github.com/Ctrl-Alt-Tea"
    MAX_CHOICE = 7

    while True:
        # Display Welcome Banner
        print(f"\033]8;;{url}\a{COLORS['BLUE']}Follow this dev on GitHub{COLORS['RESET']}\033]8;;\a")

        # Automatically display System Info on launch
        display_system_info() 

        display_menu()

        try:
            choice_input = input(f"Enter choice (1–{MAX_CHOICE + 1}): ")
            if not choice_input.strip():
                continue
            
            choice = int(choice_input)
            
            if choice == 7:
                print(" ")
                print(f"\n{COLORS['YELLOW']}Goodbye and stay awesome ...{COLORS['RESET']}")
                print(f"\033]8;;{url}\a{COLORS['BLUE']}Follow this dev on GitHub{COLORS['RESET']}\033]8;;\a")
                print(" ")
                sys.exit()

            if choice == 8:
                os.system("clear")
                sys.exit()

            command = get_scan_options(choice)
            is_dry_run = (choice == 5)
            is_search = (choice == 6)

            # Handle search input
            if is_search:
                search_term = input(f"{COLORS['CYAN']}Enter package name to search: {COLORS['RESET']}")
                if search_term:
                    command.append(search_term)
                else:
                    print(f"{COLORS['ORANGE']}Search term cannot be empty.{COLORS['RESET']}")
                    continue
            
            if command:
                # Pass both flags to run_update
                run_update(command, dry_run=is_dry_run, is_search=is_search)
            else:
                if choice not in [6, 7]:
                    print("Invalid option selected.")

        except ValueError:
            print(f"Enter a number between 1–{MAX_CHOICE + 1}")
        except KeyboardInterrupt:
            print("\nGoodbye...")
            sys.exit()

# ──────────────────────────────────────────────
if __name__ == "__main__":
    main()
