import os
import sys

# Add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import and run the app
from example.app import app

if __name__ == '__main__':
    app.run(debug=True)
