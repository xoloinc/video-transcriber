"""
Setup-fil för py2app (macOS)
Kör: python setup_mac.py py2app
"""

from setuptools import setup

APP = ['transcriber.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': None,  # Lägg till .icns-fil här om du vill ha ikon
    'plist': {
        'CFBundleName': 'Video till Undertexter',
        'CFBundleDisplayName': 'Video till Undertexter',
        'CFBundleGetInfoString': 'Transkribera video till undertexter med Whisper',
        'CFBundleIdentifier': 'com.videotranscriber.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'MIT License',
        'NSHighResolutionCapable': True,
    },
    'packages': ['openai', 'tkinterdnd2'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
