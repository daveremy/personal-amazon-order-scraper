#!/bin/bash

# Activate the virtual environment
source /Users/dremy/.virtualenvs/personal-amazon-order-scraper-ldgb/bin/activate

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller is not installed in the virtual environment."
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Run PyInstaller to create the executable
/Users/dremy/.virtualenvs/personal-amazon-order-scraper-ldgb/bin/python -m PyInstaller --onefile main.py

# Move the executable to ~/bin
mv dist/main ~/bin/paos

# Deactivate the virtual environment
deactivate

# Check if ~/bin is in the PATH
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    echo "~/bin is not in your PATH."

    read -p "Would you like to add ~/bin to your PATH? (y/n) " choice
    case "$choice" in
        y|Y )
            # Determine the shell configuration file
            if [ -n "$ZSH_VERSION" ]; then
                shell_config="$HOME/.zshrc"
            elif [ -n "$BASH_VERSION" ]; then
                shell_config="$HOME/.bashrc"
            else
                shell_config="$HOME/.profile"
            fi

            # Add ~/bin to the PATH in the shell configuration file
            echo 'export PATH="$HOME/bin:$PATH"' >> "$shell_config"
            echo "~/bin has been added to your PATH in $shell_config."
            echo "Please restart your terminal or run 'source $shell_config' to apply the changes."
            ;;
        * )
            echo "Please add ~/bin to your PATH manually to use 'paos' from anywhere."
            ;;
    esac
fi

echo "Packaging complete. The executable has been moved to ~/bin as 'paos'."
