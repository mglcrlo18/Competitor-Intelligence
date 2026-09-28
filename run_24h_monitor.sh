#!/bin/bash
# -------------------------------------------------------------
# 24-Hour Autonomous Competitor Intelligence Monitor
# Runs the Python monitor script in the background
# -------------------------------------------------------------

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

python3 daemon_24h.py
