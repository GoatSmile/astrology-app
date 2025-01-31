#!/bin/zsh

# Navigate to project
cd ~/astrology-app || { echo "Error: Can't find directory"; exit 1; }

# Activate virtual env
if [ -f "astrology-env/bin/activate" ]; then
    source astrology-env/bin/activate
else
    echo "Error: Virtual environment not found"
    exit 1
fi

# Run app with status messages
echo "Starting Streamlit app..."
streamlit run app.py