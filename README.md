[![Python package](https://github.com/Ctrl-Alt-Tea/Apt-Updater/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/Ctrl-Alt-Tea/Apt-Updater/actions/workflows/python-package.yml)

# 🚀 Apt-Updater: A Lightweight CLI UI for APT Maintenance

A powerful, colorful, and interactive command-line interface designed to streamline common APT maintenance tasks (update, upgrade, autoremove) on Debian-based systems (Ubuntu, Raspberry Pi OS, etc.).

**Simple. Fast. No bloated UI — just the essentials.**

---

## ✨ Key Features

* **System Overview:** Shows critical system information on startup (OS, Kernel, Disk Usage).
* **Core Management:** Update package lists, upgrade installed packages, and remove unused dependencies.
* **Package Search:** **Search for available packages (`apt-cache search`)** using the new Option 5.
* **Dry Run:** Preview upgrades without making system changes.
* **CLI Polish:** Clean layout with ANSI color formatting, progress bar indicators, and terminal hyperlinks (OSC8).

## 📦 Requirements

| Requirement | Status | Notes |
| :--- | :--- | :--- |
| **Python** | ✅ 3.9+ | Tested against Python 3.9, 3.10, 3.11, 3.12. |
| **Operating System** | ✅ | APT-based OS (Debian, Ubuntu, Raspberry Pi OS, etc.) |
| **Privileges** | ⚠️ `sudo` | Required to execute update, upgrade, and autoremove commands. |

## 🔧 Installation

Follow these steps to quickly clone and run the utility:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Ctrl-Alt-Tea/Apt-Updater.git](https://github.com/Ctrl-Alt-Tea/Apt-Updater.git)
    ```
2.  **Navigate to the directory:**
    ```bash
    cd Apt-Updater
    ```
3.  **Run the script:**
    ```bash
    python3 aptUpdater.py
    ```

> 💡 **Tip 1:** To make the script executable directly and avoid typing `python3`, you can run `chmod +x aptUpdater.py` and then execute it via `./aptUpdater.py`.
> 
> 💡 **Tip 2:** By adding an alias you can run this using your preffered command such as "update"

## 🖥️ Usage Menu

The script displays a numbered menu. Enter the corresponding number to execute the command.

| Option | Action | APT Command(s) |
| :---: | :--- | :--- |
| **1** | Update package lists | `sudo apt-get update` |
| **2** | Upgrade installed packages | `sudo apt-get upgrade` |
| **3** | Remove unused dependencies | `sudo apt-get autoremove` |
| **4** | Preview upgrade (Dry Run) | `sudo apt-get upgrade --dry-run` |
| **5** | Search for a package | `sudo apt-cache search <term>` |
| **6** | Exit | *(Exits normally)* |
| **7** | Exit and clear terminal | *(Exits and clears screen)* |

<img width="605" height="527" alt="A screenshot of the Apt Updater CLI UI running on a Linux terminal, showing the system information and the numbered menu options." src="https://github.com/user-attachments/assets/23fc9044-9613-4d13-a759-dd2a8db4e2f1" />


## ⚡ Future Plans

* Add `dist-upgrade` option 🔥
* Log updates to file 🚧
* Turn into a `pip`-installable tool 👑

---

Built by [Dylan Rose](https://roses.net.za/), Powered by Python
