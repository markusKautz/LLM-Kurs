@echo off
chcp 65001 >nul
title LLM-Kurs
cd /d "%~dp0"

echo.
echo  LLM-Kurs wird gestartet ...
echo.

where docker >nul 2>&1
if errorlevel 1 (
    echo  Docker ist auf diesem Rechner nicht installiert.
    echo  Bitte installiere Docker Desktop oder frag deinen Ausbilder.
    goto fehler
)

docker info >nul 2>&1
if errorlevel 1 (
    echo  Docker Desktop läuft noch nicht.
    echo  Starte Docker Desktop, warte bis unten links "Engine running" steht,
    echo  und starte diese Datei dann noch einmal.
    goto fehler
)

echo  Schritt 1 von 3: Kursumgebung vorbereiten.
echo  Beim allerersten Mal lädt Docker etwa 1 GB herunter. Das dauert ein paar Minuten.
echo.
docker build --tag llm-kurs .
if errorlevel 1 (
    echo.
    echo  Die Kursumgebung konnte nicht gebaut werden. Besteht eine Internetverbindung?
    goto fehler
)

echo.
echo  Schritt 2 von 3: Jupyter starten.
docker rm --force llm-kurs >nul 2>&1
docker run --detach --name llm-kurs --publish 127.0.0.1:8888:8888 --volume "%~dp0notebooks:/kurs/notebooks" llm-kurs >nul
if errorlevel 1 (
    echo.
    echo  Jupyter konnte nicht gestartet werden.
    echo  Vielleicht ist Port 8888 schon belegt, zum Beispiel durch ein anderes Jupyter.
    goto fehler
)

echo  Schritt 3 von 3: Warten, bis Jupyter bereit ist ...
for /l %%i in (1,1,60) do (
    curl --silent --output nul http://localhost:8888/api && goto bereit
    ping -n 2 127.0.0.1 >nul
)
echo  Jupyter antwortet nicht. Die Meldungen von Jupyter:
docker logs llm-kurs
goto fehler

:bereit
start "" http://localhost:8888/lab
echo.
echo  Fertig! Der Kurs ist im Browser geöffnet: http://localhost:8888/lab
echo.
echo  Deine Arbeit wird im Ordner "notebooks" auf diesem Rechner gespeichert.
echo  Zum Beenden: Doppelklick auf "Kurs beenden.bat".
echo.
pause
exit /b 0

:fehler
echo.
pause
exit /b 1
