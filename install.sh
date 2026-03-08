#!/bin/bash
# Created by Dylan Rose

# Define the target directory and alias
TARGET_DIR="$HOME/.local/bin/Apt-Updater"
ALIAS_NAME="update"
ALIAS_LINE="alias $ALIAS_NAME='python3 $TARGET_DIR/aptUpdater.py'"

echo "Setting up Apt-Updater..."

# Create directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Copy the python script to the target
cp aptUpdater.py "$TARGET_DIR/"
chmod +x "$TARGET_DIR/aptUpdater.py"

# Function to add alias to a shell config file
add_alias_to_config() {
    local config_file=$1
    if [ -f "$config_file" ]; then
        if ! grep -q "alias $ALIAS_NAME=" "$config_file"; then
            echo "" >> "$config_file"
            echo "# Apt-Updater Alias" >> "$config_file"
            echo "$ALIAS_LINE" >> "$config_file"
            echo "Alias '$ALIAS_NAME' added to $config_file"
        else
            echo "Alias '$ALIAS_NAME' already exists in $config_file, skipping."
        fi
    fi
}

# Add alias to .bashrc (Bash)
add_alias_to_config "$HOME/.bashrc"

# Add alias to .zshrc (Zsh)
add_alias_to_config "$HOME/.zshrc"

echo "----------------------------------------------------------------"
echo "Setup complete."
echo "Please run 'source ~/.bashrc' (or ~/.zshrc) or restart your terminal."
echo "Then you can use the '$ALIAS_NAME' command to start Apt-Updater."
echo "----------------------------------------------------------------"
