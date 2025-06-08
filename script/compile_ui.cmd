@echo off
setlocal enabledelayedexpansion

:: Get script directory and resolve paths
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%..\.venv"
set "UI_DIR=%SCRIPT_DIR%..\qwindow"
set "PYUIC=%VENV_DIR%\Scripts\pyside6-uic.exe"

:: Check if PyUIC exists
if not exist "%PYUIC%" (
    echo Error: PyUIC not found at %PYUIC%
    echo Please ensure PySide6 is installed in your virtual environment
    echo Current paths:
    echo SCRIPT_DIR: %SCRIPT_DIR%
    echo VENV_DIR: %VENV_DIR%
    echo PYUIC: %PYUIC%
    exit /b 1
)

:: Create array of UI files to compile
set "UI_FILES[0]=MainWindow.ui"
set "UI_FILES[1]=BatchContent.ui"
set "UI_FILES[2]=BatchCode.ui"
set "UI_FILES[3]=SettingsModel.ui"
set "UI_FILES[4]=SettingsPrompt.ui"

:: Compile each UI file
for /l %%i in (0,1,4) do (
    set "UI_FILE=!UI_FILES[%%i]!"
    set "OUT_FILE=!UI_FILE:.ui=_ui.py!"
    
    echo Compiling !UI_FILE!...
    "%PYUIC%" "%UI_DIR%\!UI_FILE!" -o "%UI_DIR%\!OUT_FILE!"
    
    if errorlevel 1 (
        echo Error: Failed to compile !UI_FILE!
        exit /b 1
    )
)

echo UI compilation completed successfully
exit /b 0