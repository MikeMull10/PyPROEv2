# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import os

# Function to collect all files in a directory
def collect_files_in_directory(src_dir, dest_dir):
    collected_files = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            # Calculate the relative path to maintain directory structure
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, src_dir)
            collected_files.append((full_path, os.path.join(dest_dir, os.path.dirname(relative_path))))
    return collected_files

# Initialize the datas list
datas = [
    ('algorithms', 'algorithms'),
    ('PyPROE.ico', '.'),
    ('html/about.html', 'html'),
    ('html/help.html', 'html'),
    ('components', 'components'),
    ('handlers', 'handlers'),
    ('html', 'html'),
    ('pages', 'pages'),
]

# Add all files from the assets directory
assets_directory = "assets"
datas += collect_files_in_directory(assets_directory, 'assets')

print(f"Assets: {datas}")

imports = ['PySide6', 'scipy', 'sympy', 'qtawesome', 'pyqtgraph', 'matplotlib', 'platypus', 'platypus-opt', 'PySide6.QtWebEngineWidgets', 'pymoo']

binaries = []
hiddenimports = []

for _import in imports:
    tmp_ret = collect_all(_import)
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
    

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='PyPROE',
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
    icon=['PyPROE.ico'],
    single_file=True,
    version='version.txt',
)
