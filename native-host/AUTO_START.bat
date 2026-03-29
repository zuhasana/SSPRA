@echo off
title SSERA Privacy Engine Setup

echo ==========================================
echo   SSERA PRIVACY ENGINE LAUNCHER
echo ==========================================

echo [1/3] Installing dependencies...
pip install --upgrade fastapi uvicorn presidio-analyzer presidio-anonymizer spacy

echo [2/3] Installing spaCy model...
python -m spacy download en_core_web_lg

echo [3/3] Starting server...
python server.py

pause