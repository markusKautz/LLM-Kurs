@echo off
chcp 65001 >nul
title LLM-Kurs
echo.
echo  LLM-Kurs wird beendet ...
docker stop llm-kurs >nul 2>&1
echo  Erledigt. Deine Arbeit ist im Ordner "notebooks" gespeichert.
echo.
pause
