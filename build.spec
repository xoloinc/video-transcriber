# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec-fil
Kör: pyinstaller build.spec
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Samla data-filer
datas = []
datas += collect_data_files('tkinterdnd2')

# ffmpeg-binär läggs till via workflow (finns i ./ffmpeg eller ./ffmpeg.exe)
binaries_list = []
if os.path.exists('ffmpeg'):
    binaries_list.append(('ffmpeg', '.'))
    print(f"=== Inkluderar ffmpeg: {os.path.getsize('ffmpeg')/1024/1024:.1f} MB ===")
elif os.path.exists('ffmpeg.exe'):
    binaries_list.append(('ffmpeg.exe', '.'))
    print(f"=== Inkluderar ffmpeg.exe: {os.path.getsize('ffmpeg.exe')/1024/1024:.1f} MB ===")
else:
    print("=== VARNING: Ingen ffmpeg-binär hittad! ===")

# Samla submoduler
hiddenimports = collect_submodules('openai')

a = Analysis(
    ['transcriber.py'],
    pathex=[],
    binaries=binaries_list,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['imageio_ffmpeg'],
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True if sys.platform == 'darwin' else False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# macOS: Skapa .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='Video till Undertexter.app',
        icon=None,
        bundle_identifier='com.videotranscriber.app',
        info_plist={
            'NSHighResolutionCapable': True,
            'CFBundleShortVersionString': '1.0.0',
        },
    )
