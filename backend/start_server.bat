@echo off
echo Запуск Admission Analysis System...
echo.

cd /d "%~dp0"

echo Проверка Python...
C:\PROGRA~1\Python313\python.exe --version

echo.
echo Запуск сервера Django...
C:\PROGRA~1\Python313\python.exe manage.py runserver 127.0.0.1:8000

pause