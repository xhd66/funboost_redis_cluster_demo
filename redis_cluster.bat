@echo off
cd /d "%~dp0"
powershell.exe -ExecutionPolicy Bypass -File "redis_cluster.ps1"
pause