#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -x .venv/bin/python ]]; then
  echo "Creating venv..."
  python3 -m venv .venv
fi

echo "Installing requirements..."
.venv/bin/python -m pip install -r requirements.txt

echo "Starting API + Streamlit..."
exec .venv/bin/python run.py
