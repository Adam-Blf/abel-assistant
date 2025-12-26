@echo off
title A.B.E.L - Launcher
color 0B

echo.
echo  ======================================
echo     A.B.E.L - Autonomous Backend
echo        Entity for Living v2.0
echo  ======================================
echo.

:: Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker n'est pas en cours d'execution.
    echo         Veuillez demarrer Docker Desktop.
    echo.
    pause
    exit /b 1
)

echo [OK] Docker detecte
echo.

:: Menu
:menu
echo  Que voulez-vous faire?
echo.
echo  [1] Demarrer A.B.E.L (Docker Compose)
echo  [2] Arreter A.B.E.L
echo  [3] Voir les logs
echo  [4] Reconstruire les conteneurs
echo  [5] Ouvrir le Dashboard (localhost:3000)
echo  [6] Ouvrir l'API Docs (localhost:8000/docs)
echo  [7] Quitter
echo.
set /p choice="Votre choix: "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto logs
if "%choice%"=="4" goto rebuild
if "%choice%"=="5" goto dashboard
if "%choice%"=="6" goto api
if "%choice%"=="7" goto quit

echo Choix invalide.
goto menu

:start
echo.
echo [INFO] Demarrage de A.B.E.L...
docker-compose up -d
echo.
echo [OK] A.B.E.L est demarre!
echo     - API: http://localhost:8000
echo     - Docs: http://localhost:8000/docs
echo     - Dashboard: http://localhost:3000
echo.
pause
goto menu

:stop
echo.
echo [INFO] Arret de A.B.E.L...
docker-compose down
echo [OK] A.B.E.L est arrete.
echo.
pause
goto menu

:logs
echo.
echo [INFO] Affichage des logs (Ctrl+C pour quitter)...
docker-compose logs -f
goto menu

:rebuild
echo.
echo [INFO] Reconstruction des conteneurs...
docker-compose build --no-cache
docker-compose up -d
echo [OK] Reconstruction terminee!
echo.
pause
goto menu

:dashboard
echo.
echo [INFO] Ouverture du Dashboard...
start http://localhost:3000
goto menu

:api
echo.
echo [INFO] Ouverture de la documentation API...
start http://localhost:8000/docs
goto menu

:quit
echo.
echo Au revoir!
exit /b 0
