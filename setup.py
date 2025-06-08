import os
import sys

from PySide6 import QtCore
from cx_Freeze import setup, Executable

import constant

# Find Qt plugins and binaries directories
qt_binaries_dir = os.path.dirname(QtCore.__file__)
qt_plugins_dir = os.path.join(qt_binaries_dir, "plugins")

# Create include_files list with required Qt plugin directories
include_files = []

# Add all Qt plugins
for plugin_type in ["platforms", "styles", "imageformats", "platformthemes", "accessible", "iconengines", "sqldrivers"]:
    plugin_dir = os.path.join(qt_plugins_dir, plugin_type)
    if os.path.exists(plugin_dir):
        include_files.append((plugin_dir, os.path.join("lib", "PySide6", "plugins", plugin_type)))

# Add essential Qt DLLs directly
for dll_file in os.listdir(qt_binaries_dir):
    if dll_file.endswith(".dll") and os.path.isfile(os.path.join(qt_binaries_dir, dll_file)):
        include_files.append((os.path.join(qt_binaries_dir, dll_file), dll_file))

build_exe_options = {
    # Your application packages with more detailed imports
    "packages": ["PySide6", "requests", "PIL", "loguru", "pydantic", "anthropic", "openai"],
    # Your application modules
    "includes": ["qwidget", "entity", "constant", "impl", "util", "qobject", "qwindow"],
    "excludes": ["tkinter", "unittest", "pydoc"],
    "include_files": include_files,
    # Additional Qt-specific options
    "zip_include_packages": ["PySide6"],
    "include_msvcr": True,
    "no_compress": True,
    # Add this option to include all modules in the dependency analysis
    "optimize": 0,
}

base = "Console" if sys.platform == "win32" else None

setup(
    name=constant.APPLICATION,
    version=constant.VERSION,
    description=constant.DESCRIPTION,
    options={"build_exe": build_exe_options},
    executables=[Executable(
        script="main.py",
        base=base,
        target_name=constant.APPLICATION + ".exe",
        icon="icon.ico" if os.path.exists("icon.ico") else None
    )]
)
