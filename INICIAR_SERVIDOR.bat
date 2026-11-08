@echo off
chcp 65001 >nul
title PC Remote - Servidor
cd /d "%~dp0"

echo ============================================
echo   PC Remote Control - Servidor
echo ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [ERRO] Python nao encontrado.
  echo Instale em https://www.python.org/downloads/ e marque "Add Python to PATH".
  echo.
  pause
  exit /b 1
)

echo Instalando dependencias (so demora na primeira vez)...
python -m pip install -r requirements.txt
echo.

set /p TOKEN=Defina uma senha de acesso (ex: minhaSenha123):
if "%TOKEN%"=="" set TOKEN=minhaSenha123

echo.
echo Descobrindo seu IP local...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do echo    No celular use:  ws://%%a:8765
echo.
echo Iniciando servidor (feche esta janela para parar)...
echo.
python server.py --token %TOKEN%

pause
