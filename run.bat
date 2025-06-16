@echo off
REM Startup script for Elevator Fuzzy Control System
REM Projeto de Sistemas Embarcados - INATEL

echo ================================================================
echo     SISTEMA DE CONTROLE FUZZY PARA ELEVADOR
echo     Projeto de Sistemas Embarcados - INATEL
echo     Baseado no Elevador VILLARTA Standard COMPAQ Slim
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python nao esta instalado ou nao esta no PATH
    echo Por favor, instale Python 3.8+ e tente novamente
    pause
    exit /b 1
)

echo Python encontrado. Verificando dependencias...

REM Check if requirements are installed
python -c "import fastapi, uvicorn, numpy, matplotlib, skfuzzy" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando dependencias necessarias...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Erro na instalacao das dependencias
        pause
        exit /b 1
    )
    echo Dependencias instaladas com sucesso!
    echo.
)

echo Escolha uma opcao:
echo 1. Testar apenas o controlador fuzzy
echo 2. Executar interface web completa
echo 3. Executar teste do controlador simples
echo.
set /p choice="Digite sua escolha (1-3): "

if "%choice%"=="1" (
    echo.
    echo Executando teste do controlador fuzzy...
    echo.
    python test_elevator.py
    pause
) else if "%choice%"=="2" (
    echo.
    echo Iniciando servidor web...
    echo Acesse: http://localhost:8000
    echo Pressione Ctrl+C para parar o servidor
    echo.
    python main.py
) else if "%choice%"=="3" (
    echo.
    echo Executando teste do controlador simples...
    echo.
    python simple_elevator_controller.py
    pause
) else (
    echo Opcao invalida. Executando interface web por padrao...
    echo.
    echo Iniciando servidor web...
    echo Acesse: http://localhost:8000
    echo Pressione Ctrl+C para parar o servidor
    echo.
    python main.py
)

echo.
echo Sistema finalizado.
pause
