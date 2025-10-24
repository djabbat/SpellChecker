#!/usr/bin/env python3
"""
Setup script for Georgian SpellChecker
"""

from setuptools import setup, find_packages

with open("ReadMe.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="georgian-spellchecker",
    version="1.0.0",
    author="SpellChecker Team",
    author_email="your-email@example.com",
    description="AI-based Georgian language spell checker with web interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/georgian-spellchecker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.7",
    install_requires=[
        "Flask>=2.3.3",
        "beautifulsoup4>=4.12.2", 
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "georgian-spellchecker=run_web_simple:main",
        ],
    },
)