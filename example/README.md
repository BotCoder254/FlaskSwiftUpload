# FlaskSwiftUpload Demo Application

A professional demo application showcasing the features of FlaskSwiftUpload with TailwindCSS and MongoDB.

## Prerequisites

1. Python 3.8+
2. MongoDB
3. Node.js and npm

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd example
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Node.js dependencies:
```bash
npm install
```

4. Build CSS:
```bash
npm run build
```

5. Start MongoDB:
```bash
mongod --dbpath /path/to/data/db
```

6. Run the application:
```bash
python app.py
```

## Features

- Modern UI with TailwindCSS
- Real-time upload progress
- File type detection
- Image/Video processing
- MongoDB integration
- Responsive design
- Dark mode support

## Development

For development with auto-reloading CSS:

```bash
npm run build:css
```

## Testing

1. Ensure MongoDB is running
2. Run the test suite:
```bash
pytest tests/
```

## Directory Structure

```
example/
├── app.py              # Flask application
├── templates/          # HTML templates
│   └── index.html     # Main dashboard
├── static/            # Static files
│   ├── src/          # Source files
│   │   ├── main.css  # TailwindCSS source
│   │   └── main.js   # JavaScript
│   └── dist/         # Compiled assets
├── uploads/          # Upload directory
├── tests/            # Test files
├── package.json      # Node.js dependencies
└── tailwind.config.js # TailwindCSS configuration
```

## Security Notes

- File validation is enabled
- MIME type checking
- Size limits enforced
- Malicious file detection
- Secure file storage

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
