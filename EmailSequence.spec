# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Email Sequence Manager GUI

To build the executable, run:
    pyinstaller EmailSequence.spec

This will create a standalone executable in the dist/ folder.
"""

block_cipher = None


a = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gui_config.yaml', '.'),
        ('gui', 'gui'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
        'tkcalendar',
        'pandas',
        'openpyxl',
        'yaml',
    ],
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
    name='EmailSequenceManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='gui/assets/icon.ico' if os.path.exists('gui/assets/icon.ico') else None,
)
