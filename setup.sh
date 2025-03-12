#!/bin/bash

# Setup script for Streamlit Cloud deployment

# Make sure the script is executable
chmod +x setup.sh

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p ~/.streamlit

# Create Streamlit config
echo "\
[general]
email = \"\"
" > ~/.streamlit/credentials.toml

echo "\
[server]
headless = true
enableCORS = false
port = $PORT
" > ~/.streamlit/config.toml 