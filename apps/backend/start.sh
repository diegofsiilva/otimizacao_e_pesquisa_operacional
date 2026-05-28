#!/bin/bash

set -e

BACKEND_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$BACKEND_DIR")")"
SIMPLEX_DIR="$ROOT_DIR/apps/algoritmo_simplex"

cd "$BACKEND_DIR"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r "$SIMPLEX_DIR/requirements.txt"
.venv/bin/pip install -q -r "$BACKEND_DIR/requirements.txt"

exec .venv/bin/python run_server.py