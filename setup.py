from setuptools import setup, find_packages

setup(
    name="flask-swift-upload",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Flask>=2.0.0",
        "Flask-PyMongo>=2.3.0",
        "python-magic>=0.4.27",
        "Pillow>=9.0.0",
        "ffmpeg-python>=0.2.0",
        "typing-extensions>=4.0.0",
        "aiofiles>=0.8.0"
    ],
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="Professional file upload module for Flask",
    long_description="A professional file upload module for Flask applications",
    url="https://github.com/yourusername/flask-swift-upload",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    include_package_data=True,
    zip_safe=False,
)
