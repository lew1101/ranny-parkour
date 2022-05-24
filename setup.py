import sys
from cx_Freeze import setup, Executable


base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable(
        script='./design_platformer.py',
        base=base,
        target_name='design-platformer',
    )
]

# Dependencies are automatically detected, but it might need
# fine tuning.
build_exe_options = {
    'packages': ["pygame"],
    'include_files': ["assets/", "levels/"],
    'excludes': []
}

bdist_dmg_options = {
    'applications_shortcut': True
}

bdist_mac_options = {
    'iconfile': 'assets/icons/icon.png'
}


setup(name='design-platformer',
      version='0.1.0',
      description='',
      options={
          'build_exe': build_exe_options,
          'bdist_dmg': bdist_dmg_options,
          'bdist_mac': bdist_mac_options
      },
      executables=executables)
