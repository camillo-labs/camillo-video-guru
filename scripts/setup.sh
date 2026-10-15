#!/bin/bash
# One-off setup: a local virtualenv with the Python dependencies, the Swift Vision helper (macOS) and,
# with --testdata, the self-generated test material. Needs ffmpeg and python3 on the PATH.
set -e
cd "$(dirname "$0")/.."
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
if command -v swiftc >/dev/null; then mkdir -p engine/bin && swiftc -O engine/vision.swift -o engine/bin/vision; fi
[ "$1" = "--testdata" ] && scripts/make_testdata.sh
echo "ready: .venv/bin/python engine/make_edit.py --list"
