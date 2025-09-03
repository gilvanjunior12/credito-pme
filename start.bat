@echo off
REM ---------------------------------------------------------------------------
REM Script de inicialização da API de Crédito PME
REM Ativa a venv local e sobe o servidor Uvicorn em modo desenvolvimento
REM ---------------------------------------------------------------------------
cd /d %~dp0
call .\.venv\Scripts\activate.bat
uvicorn app.main:app --reload --port 8001
