#!/bin/bash
# -------------------------------------------------------------
# Launch Competitor Intelligence Platform
# -------------------------------------------------------------

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Setup virtual environment if it does not exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing required packages..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Launch Streamlit using python module to bypass PATH issues
python3 -m streamlit run app.py
