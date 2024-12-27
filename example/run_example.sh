#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check MongoDB
echo -e "${BLUE}Checking MongoDB status...${NC}"
if ! mongosh --eval "db.runCommand({ping:1})" --quiet; then
    echo -e "${RED}MongoDB is not running. Starting MongoDB...${NC}"
    sudo systemctl start mongod
    sleep 2
    if ! mongosh --eval "db.runCommand({ping:1})" --quiet; then
        echo -e "${RED}Failed to start MongoDB. Please check the logs with: sudo journalctl -u mongod${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}MongoDB is running${NC}"

# Set up Python environment
export PYTHONPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd ):$PYTHONPATH"
source ~/flask_swift_project/venv/bin/activate

# Run the application
python app.py
