

import sys
from cx_Freeze import setup, Executable
import os

os.environ['TCL_LIBRARY'] = r'C:\Users\seoleary\AppData\Local\Continuum\anaconda3\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\seoleary\AppData\Local\Continuum\anaconda3\tcl\tk8.6'

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["tkinter", "pandas","bs4","requests","idna","numpy"],
                     "excludes": ["PyQt4.QtSql", "sqlite3", 
                                  "scipy.lib.lapack.flapack",
                                  "PyQt4.", 
                                  "PyQt5",
                                  "sklearn",
                                  "scipy",
                                  "adodbapi",
                                  "asn1crypto",
                                  "asyncio",
                                  "atomicwrites",
                                  "attr",
                                  "babel",
                                  "backcall",
                                  "backports",
                                  "bokeh",
                                  "bottleneck",
                                  "cffi"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "NSN_CAGE_tool",
        version = "0.6",
        description = "NSN CAGE lookup tool",
        options = {"build_exe": build_exe_options},
        executables = [Executable("NSN_TK_V2.py", base=base)])