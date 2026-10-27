# -*- mode: python ; coding: utf-8 -*-
#
# Builds a single executable for the GUI (app/gui_main.py).
#
#   python build_scripts/build.py        (recommended - also stages .env.example next to the exe)
#   pyinstaller bookstore.spec           (just the executable)
#
# .env is NOT bundled (`datas`): PyInstaller would pack it INSIDE the exe, where nobody can edit it, and it
# holds credentials that must not be baked into a binary. The exe reads the .env that lies next to it
# (see app/env.py).
#
# upx=False on purpose: UPX-packed executables trigger antivirus false positives noticeably more often.
# To add an icon: put a .ico file in the repo and set icon='path/to/icon.ico' in EXE(...) below.

a = Analysis(
    ['app/gui_main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BookByteStore',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
