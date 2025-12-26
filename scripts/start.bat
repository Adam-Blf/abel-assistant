@echo off
REM A.B.E.L - Start Script for Windows

echo 🤖 Starting A.B.E.L...

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found. Copying from .env.example...
    copy .env.example .env
    echo 📝 Please edit .env with your API keys before continuing.
    pause
    exit /b 1
)

REM Start Docker services
echo 🐳 Starting Docker services...
docker-compose up -d

REM Wait for services
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak

REM Check health
echo 🔍 Checking API health...
curl -s http://localhost:8000/health

echo.
echo ✅ A.B.E.L is ONLINE!
echo.
echo 📍 Access points:
echo    - API: http://localhost:8000
echo    - Docs: http://localhost:8000/docs
echo    - Adminer: http://localhost:8080
echo.
echo 🛑 To stop: docker-compose down
pause
