#!/bin/bash
# -------------------------------------------------------------------
# Native macOS App Launcher for Competitor Intelligence Platform
# Starts Streamlit in headless background mode on port 8502 and opens dedicated Cocoa window.
# -------------------------------------------------------------------

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# 1. Kill any existing instance on port 8502
lsof -ti:8502 | xargs kill -9 2>/dev/null

# 2. Check virtual environment
if [ ! -d "$DIR/venv" ]; then
    /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m venv "$DIR/venv"
    "$DIR/venv/bin/pip" install -r "$DIR/requirements.txt"
fi

# 3. Launch Streamlit headlessly using venv binary directly on localhost
"$DIR/venv/bin/streamlit" run "$DIR/app.py" --server.headless true --server.address localhost --server.port 8502 > /dev/null 2>&1 &
STREAMLIT_PID=$!

# 4. Wait until the local server responds (up to 10 seconds)
for i in {1..20}; do
    if curl -s http://localhost:8502 >/dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

# 5. Open native macOS Cocoa Window
"$DIR/Competitor_Window"

# 6. When the window is closed, terminate the background server
kill -9 $STREAMLIT_PID 2>/dev/null
