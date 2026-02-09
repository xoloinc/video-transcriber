#!/bin/bash
# Byggskript för macOS

echo "=== Video till Undertexter - Mac Build ==="

# Skapa virtual environment
echo "Skapar virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Installera beroenden
echo "Installerar beroenden..."
pip install --upgrade pip
pip install openai tkinterdnd2 imageio-ffmpeg pyinstaller

# Bygg appen
echo "Bygger .app (detta kan ta några minuter)..."
pyinstaller build.spec --clean

echo ""
echo "=== Klart! ==="
echo "Appen finns i: dist/Video till Undertexter.app"
echo ""
echo "ffmpeg är inbyggt - användaren behöver inte installera något extra!"
