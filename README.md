# Video till Undertexter

Dra och släpp en video för att automatiskt transkribera till SRT-undertexter med OpenAI Whisper.

## Krav

- Python 3.8+
- OpenAI API-nyckel

## Installation (utveckling)

```bash
# Installera Python-beroenden
pip install -r requirements.txt

# Kör appen
python transcriber.py
```

## Användning

1. Starta appen: `python transcriber.py`
2. Klistra in din OpenAI API-nyckel
3. Dra och släpp en videofil (eller klicka för att välja)
4. Vänta på transkribering
5. SRT-filen sparas i samma mapp som videon

## Bygga som Mac-app

```bash
# På Mac, kör:
chmod +x build_mac.sh
./build_mac.sh

# Appen hamnar i: dist/Video till Undertexter.app
```

**ffmpeg är inbyggt** - användaren behöver inte installera något extra!

## Bygga som Windows-app

```bash
pip install pyinstaller
pyinstaller build.spec --clean

# Appen hamnar i: dist/VideoTillUndertexter.exe
```

## Filformat som stöds

- MP4, MKV, AVI, MOV, WebM, WMV, FLV

## Storlek

Den färdiga appen är ca 100-150 MB eftersom ffmpeg är inbyggt.
