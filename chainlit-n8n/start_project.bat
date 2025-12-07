@echo off
title Start Chainlit + n8n Project
echo ==========================================
echo 🚀 Starting n8n + Chainlit environment
echo ==========================================

:: Ganti ke folder project
cd /d C:\chainlit-n8n

:: Cek apakah Docker sudah jalan
echo 🐳 Checking Docker status...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker belum berjalan!
    echo Silakan buka Docker Desktop dulu dan tunggu sampai "Docker Engine is running".
    pause
    exit /b
)

:: Jalankan container Docker
echo 🐳 Starting Docker containers...
docker compose up -d

:: Tunggu beberapa detik biar n8n siap
echo ⏳ Waiting for n8n to be ready...
timeout /t 5 >nul

:: Aktifkan virtual environment
echo 🧠 Activating Python virtual environment...
call venv\Scripts\activate

:: Jalankan Chainlit di background
echo 💬 Starting Chainlit app...
start cmd /k "title Chainlit App && chainlit run app.py"

:: Tunggu beberapa detik agar Chainlit siap
timeout /t 3 >nul

:: Buka browser otomatis
echo 🌐 Opening web interfaces...
start http://localhost:8000
start http://localhost:5678

echo ==========================================
echo ✅ All systems running!
echo ------------------------------------------
echo Chainlit: http://localhost:8000
echo n8n Dashboard: http://localhost:5678
echo ==========================================
pause
