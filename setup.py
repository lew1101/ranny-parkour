import sys
from cx_Freeze import setup, Executable

METADATA = {
    "name": "ranny-parkour",
    "version": "0.2.1",
    "description": "",
    "license": "MIT"
}


base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable(
        script='./main.py',
        base=base,
        target_name='ranny-parkour',
    )
]

# Dependencies are automatically detected, but it might need
# fine tuning.
build_exe_options = {
    'include_files': ["ranny_parkour/assets/", "ranny_parkour/levels/"],
    'excludes': []
}

bdist_dmg_options = {
    'applications_shortcut': True
}

bdist_mac_options = {
    'iconfile': 'ranny_parkour/assets/icons/icon.png',
    'bundle_name': 'Ranny Parkour'
}

setup(
    **METADATA,
    options={
        'build_exe': build_exe_options,
        'bdist_dmg': bdist_dmg_options,
        'bdist_mac': bdist_mac_options},
    executables=executables,)
