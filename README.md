Apt Updater CLI UI

A lightweight and colorful command-line interface for running common APT maintenance commands on Debian-based Linux systems (including Raspberry Pi OS).

Built by [Dylan Rose](https://roses.net.za/) & powered by Python.

🚀 Features
- ✔ Show system information
- ✔ Update package lists
- ✔ Upgrade installed packages
- ✔ Remove unused dependencies
- ✔ Exit normally or clear terminal on exit
- ✔ Clean CLI layout with ANSI color formatting
- ✔ Clickable GitHub link inside terminal (OSC8 hyperlinks)

Simple. Fast. No bloated UI — just the essentials.


📦 Requirements
- Python 3	✅
- APT-based OS (Debian, Ubuntu, Raspberry Pi OS etc.)	✅
- sudo privileges	⚠ Needed to install updates


🔧 Installation
Clone the repo:
1. git clone git@github.com:Ctrl-Alt-Tea/Apt-Updater.git
2. cd Apt-Updater


Run the script:
```
python3 aptUpdater.py
```
or setup an alias in .bashrc


<img width="587" height="503" alt="image" src="https://github.com/user-attachments/assets/2adf47d9-fc37-40b2-9fd4-190813486790" />



🖥 Usage Menu
1. Update packages and sources
2. Upgrade packages
3. Remove uneeded dependencies
4. Preview upgrade (See what would change)
5. Exit
6. Exit and clear terminal



⚡ To-Do / Potential Future Addons
- Add dist-upgrade option	🔥 Possible
- Log updates to file	🚧 Maybe soon
- ~~Add progress bars~~ (Added in V1.1.0)
- Turn into pip-installable tool	👑 Would be awesome



[My Github Profile](https://github.com/Ctrl-Alt-Tea)
