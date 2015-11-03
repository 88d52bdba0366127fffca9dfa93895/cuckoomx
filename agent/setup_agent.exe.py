#!/usr/bin/env python
# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

exe = Executable(
    script = "agent.py",
    base = base,
)

options = dict(
    excludes = ['Tkinter']
)

setup(
    name = "agent.exe",
    version = "1.2",
    description = "Cuckoo Sandbox - a malware analysis system",
    options={'build_exe': options},
    executables = [exe])