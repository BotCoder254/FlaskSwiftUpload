#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Setting up FlaskSwiftUpload Demo${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install main module
echo -e "${GREEN}Installing FlaskSwiftUpload module...${NC}"
pip install -e .

# Install example dependencies
echo -e "${GREEN}Installing example dependencies...${NC}"
cd example
pip install -r requirements.txt

# Install and build frontend
echo -e "${GREEN}Setting up frontend...${NC}"
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is not installed. Please install Node.js and npm first.${NC}"
    exit 1
fi

npm install
npm run build

# Create required directories
echo -e "${GREEN}Creating required directories...${NC}"
mkdir -p uploads static/dist

# Check MongoDB
echo -e "${GREEN}Checking MongoDB status...${NC}"
if ! systemctl is-active --quiet mongodb; then
    echo -e "${RED}MongoDB is not running. Please start it with: sudo service mongodb start${NC}"
    exit 1
fi

# Start the application
echo -e "${GREEN}Starting Flask application...${NC}"
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --port 5000
