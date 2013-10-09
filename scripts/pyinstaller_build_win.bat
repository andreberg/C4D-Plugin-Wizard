@echo off

set python_exe="C:\Python27\python.exe"
set pyinstaller_2_py="C:\Users\Andre\source\python\pyinstaller-2.0\pyinstaller.py"
set root=C:\Users\Andre\Documents\Eclipse\Projects\Python\C4D Plugin Wizard

%python_exe%  %pyinstaller_2_py% "%root%\scripts\C4D Plugin Wizard.spec"

pause