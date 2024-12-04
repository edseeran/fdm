#!/bin/bash

# Define log file
LOG_FILE="/var/log/data-extract.log"

# Function to log messages with date
log_message() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

# Debugging output
echo "Script started at: $(date)"

# Clear log file, to see the most recent log only
# > "$LOG_FILE"

# Export PATH
export PATH="/usr/local/bin:/usr/bin:/bin"

# Set the path to the virtual environment
VENV_DIR="/var/www/html/ipm-enterprise/backend/venv"

# Debugging output
echo "Virtual environment directory: $VENV_DIR"

# Navigate to the backend project directory
echo "Navigating to the backend project directory..."
cd /var/www/html/ipm-enterprise/backend || exit
echo "Current directory: $(pwd)"

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Debugging output
echo "Current directory after activation: $(pwd)"

# Navigate to the 'ipment' directory and run the Django management command
echo "Navigating to ipment directory and running Django command..."
cd /var/www/html/ipm-enterprise/backend/ipment || exit
if python3 manage.py bir; then
    log_message "Django command executed successfully"
    echo "Django command executed successfully"
else
    log_message "Django command execution failed"
    echo "Django command execution failed"
fi

# Debugging output
echo "Script finished at: $(date)"