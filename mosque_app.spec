# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['mosque_app.py'],
    pathex=[],
    binaries=[],
    datas=[('background.jpg', '.'), ('adhan.wav', '.'), ('close.png', '.'), ('minimize.png', '.'), ('meknes_prayer_all.csv', '.'), ('mosque.ico', '.')],
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
    name='mosque_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['mosque.ico'],
)
