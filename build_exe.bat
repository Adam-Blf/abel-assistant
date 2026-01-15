@echo off
title A.B.E.L - Build EXE
color 0B

echo.
echo  ======================================
echo     A.B.E.L - Build Executable
echo  ======================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python n'est pas installe.
    pause
    exit /b 1
)
echo [OK] Python detecte

:: Install PyInstaller if needed
echo [INFO] Installation de PyInstaller...
pip install pyinstaller --quiet

:: Build the executable
echo [INFO] Construction de l'executable...
pyinstaller --onefile --noconsole --name "ABEL_Launcher" --icon=frontend/public/favicon.ico launcher.py

if exist "dist\ABEL_Launcher.exe" (
    echo.
    echo [OK] Executable cree avec succes!
    echo     Emplacement: dist\ABEL_Launcher.exe
    echo.

    :: Copy to root
    copy "dist\ABEL_Launcher.exe" "ABEL_Launcher.exe" >nul
    echo [OK] Copie dans le dossier racine.
) else (
    echo [ERROR] Echec de la creation de l'executable.
)

echo.
pause
