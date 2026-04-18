@echo off
REM Quick setup script for AI Mail Assistant Frontend (Windows)

echo.
echo 🚀 AI Mail Assistant Frontend Setup
echo ====================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js is not installed. Please install it first.
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js %NODE_VERSION% detected

REM Change to frontend directory
cd /d "%~dp0frontend" || exit /b 1

REM Install dependencies
echo.
echo 📦 Installing dependencies...
call npm install

REM Create .env file if it doesn't exist
if not exist .env (
    echo.
    echo 📝 Creating .env file...
    copy .env.example .env
    echo ✅ .env created. Update it with your configuration:
    echo    - VITE_API_URL=http://localhost:8000/api
)

echo.
echo ✅ Setup complete!
echo.
echo 📋 Next steps:
echo    1. Start the backend: cd backend ^&^& python manage.py runserver
echo    2. Start the frontend: cd frontend ^&^& npm run dev
echo    3. Open http://localhost:3000 in your browser
echo.
echo 🎉 Happy coding!
echo.
pause
