#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Starting FlaskSwiftUpload Demo${NC}"

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo -e "${GREEN}Starting MongoDB...${NC}"
    sudo service mongodb start
    sleep 2  # Wait for MongoDB to start
fi

# Verify MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo -e "${RED}Failed to start MongoDB. Please start it manually with: sudo service mongodb start${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source ../venv/bin/activate

# Install requirements if needed
if [ ! -f "venv/lib/python*/site-packages/flask_pymongo.py" ]; then
    echo -e "${GREEN}Installing requirements...${NC}"
    pip install -r requirements.txt
fi

# Build frontend assets
if [ ! -d "node_modules" ]; then
    echo -e "${GREEN}Installing Node.js dependencies...${NC}"
    npm install
fi

echo -e "${GREEN}Building frontend assets...${NC}"
npm run build

# Create upload directory if it doesn't exist
mkdir -p uploads

# Start Flask application
echo -e "${GREEN}Starting Flask application...${NC}"
export FLASK_APP=app.py
export FLASK_ENV=development

python -m flask run --host=0.0.0.0 --port=5000
