#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Project directories
VENDOR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$HOME/flask_swift_project"
MODULE_NAME="flask_swift_upload"

echo -e "${BLUE}Setting up FlaskSwiftUpload Development Environment${NC}"

# Function to check if a command was successful
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
        exit 1
    fi
}

# Install system dependencies
echo -e "\n${BLUE}Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y python3-full python3-pip python3-venv libmagic1 ffmpeg gnupg curl
check_status "System dependencies installed"

# Setup MongoDB
echo -e "\n${BLUE}Setting up MongoDB...${NC}"
if ! command -v mongod &> /dev/null; then
    echo "Installing MongoDB..."
    # Import MongoDB public key
    curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
        sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
        --dearmor
    check_status "MongoDB key imported"

    # Create list file for MongoDB
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
        sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    check_status "MongoDB repository added"

    sudo apt-get update
    sudo apt-get install -y mongodb-org
    check_status "MongoDB packages installed"

    # Start MongoDB
    sudo systemctl daemon-reload
    sudo systemctl start mongod
    sudo systemctl enable mongod
    check_status "MongoDB started and enabled"

    # Wait for MongoDB to be ready
    echo "Waiting for MongoDB to be ready..."
    sleep 5
else
    echo "MongoDB already installed, ensuring service is running..."
    sudo systemctl start mongod
    sudo systemctl enable mongod
fi

# Verify MongoDB is running
echo "Verifying MongoDB connection..."
if ! mongosh --eval "db.runCommand({ping:1})" --quiet; then
    echo -e "${RED}Failed to connect to MongoDB. Please check the logs with: sudo journalctl -u mongod${NC}"
    exit 1
fi
check_status "MongoDB is running and accessible"

# Create project directory
echo -e "\n${BLUE}Setting up project directory...${NC}"
mkdir -p "$PROJECT_DIR"
check_status "Project directory created"

# Create and activate virtual environment
echo -e "\n${BLUE}Setting up Python virtual environment...${NC}"
cd "$PROJECT_DIR"
python3 -m venv venv
source venv/bin/activate
check_status "Virtual environment created and activated"

# Upgrade pip
echo -e "\n${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip
check_status "Pip upgraded"

# Install Python dependencies
echo -e "\n${BLUE}Installing Python dependencies...${NC}"
pip install Flask Flask-PyMongo python-magic Pillow ffmpeg-python typing-extensions aiofiles pytest pytest-asyncio pytest-cov
check_status "Python dependencies installed"

# Create symbolic link for development
echo -e "\n${BLUE}Setting up module for development...${NC}"
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
ln -sf "$VENDOR_DIR/$MODULE_NAME" "$SITE_PACKAGES/"
check_status "Module symbolic link created"

# Set up example application
echo -e "\n${BLUE}Setting up example application...${NC}"
cd "$VENDOR_DIR/example"
mkdir -p uploads/backup static/dist
check_status "Example directories created"

# Create run script with MongoDB check
cat > "$VENDOR_DIR/example/run_example.sh" << 'EOL'
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
EOL

chmod +x "$VENDOR_DIR/example/run_example.sh"
check_status "Run script created"

echo -e "\n${GREEN}Setup completed successfully!${NC}"
echo -e "\nTo run the example application:"
echo -e "1. cd $VENDOR_DIR/example"
echo -e "2. ./run_example.sh"
echo -e "\nThe application will be available at http://localhost:5000"
