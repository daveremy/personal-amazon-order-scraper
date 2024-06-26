#!/bin/bash

# Activate the virtual environment
source /Users/dremy/.virtualenvs/personal-amazon-order-scraper-ldgb/bin/activate

# Run PyInstaller to create the executable
/Users/dremy/.virtualenvs/personal-amazon-order-scraper-ldgb/bin/python -m PyInstaller --onefile main.py

# Move the executable to ~/bin
mv dist/main ~/bin/paos

# Deactivate the virtual environment
deactivate

echo "Packaging complete. The executable has been moved to ~/bin as 'paos'."

