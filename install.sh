#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Installing FlaskSwiftUpload${NC}"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Install system dependencies
echo -e "${GREEN}Installing system dependencies...${NC}"
if [ -f /etc/debian_version ]; then
    sudo apt-get update
    sudo apt-get install -y libmagic1 ffmpeg
elif [ -f /etc/redhat-release ]; then
    sudo yum install -y file-devel ffmpeg
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${GREEN}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Install the package in development mode
echo -e "${GREEN}Installing FlaskSwiftUpload in development mode...${NC}"
pip install -e .

echo -e "${GREEN}Installation complete!${NC}"
echo -e "You can now run the example application with: ${BLUE}./run_demo.sh${NC}"
