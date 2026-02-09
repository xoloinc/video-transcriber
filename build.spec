# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec-fil - fungerar på Mac, Windows och Linux
Kör: pyinstaller build.spec
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Samla alla nödvändiga data-filer
datas = []
datas += collect_data_files('tkinterdnd2')
datas += collect_data_files('imageio_ffmpeg')  # Inkluderar ffmpeg-binären!

# Samla submoduler
hiddenimports = []
hiddenimports += collect_submodules('openai')
hiddenimports += ['imageio_ffmpeg']

a = Analysis(
    ['transcriber.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VideoTillUndertexter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Ingen terminal-fönster
    disable_windowed_traceback=False,
    argv_emulation=True if sys.platform == 'darwin' else False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# macOS-specifik: Skapa .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='Video till Undertexter.app',
        icon=None,  # Lägg till .icns här
        bundle_identifier='com.videotranscriber.app',
        info_plist={
            'NSHighResolutionCapable': True,
            'CFBundleShortVersionString': '1.0.0',
        },
    )
