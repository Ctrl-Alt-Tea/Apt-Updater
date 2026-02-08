#!/bin/bash
# Created by Dylan Rose

# Define the target directory and alias
TARGET_DIR="$HOME/.local/bin/Apt-Updater"
ALIAS_LINE="alias update='python3 $TARGET_DIR/aptUpdater.py'"

echo "Setting up Apt-Updater..."

# Create directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Copy the python script to the target
cp aptUpdater.py "$TARGET_DIR/"
chmod +x "$TARGET_DIR/aptUpdater.py"

# Add alias to .bashrc only if it doesn't already exist
if ! grep -q "alias update=" ~/.bashrc; then
    echo "$ALIAS_LINE" >> ~/.bashrc
    echo "Alias 'update' added to .bashrc"
else
    echo "Alias 'update' already exists, skipping."
fi

echo "Setup complete. Please run 'source ~/.bashrc' or restart your terminal."
