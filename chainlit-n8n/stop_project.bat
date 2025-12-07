@echo off
title Stop Chainlit + n8n Project
echo ==========================================
echo 🛑 Stopping Docker and Chainlit environment
echo ==========================================

:: Stop Docker containers
docker compose down

:: Info
echo Semua container telah dimatikan dengan aman.
pause
