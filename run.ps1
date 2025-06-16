# Startup script for Elevator Fuzzy Control System
# Projeto de Sistemas Embarcados - INATEL

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "    SISTEMA DE CONTROLE FUZZY PARA ELEVADOR" -ForegroundColor Yellow
Write-Host "    Projeto de Sistemas Embarcados - INATEL" -ForegroundColor White
Write-Host "    Baseado no Elevador VILLARTA Standard COMPAQ Slim" -ForegroundColor White
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion encontrado" -ForegroundColor Green
} catch {
    Write-Host "✗ Erro: Python não está instalado ou não está no PATH" -ForegroundColor Red
    Write-Host "Por favor, instale Python 3.8+ e tente novamente" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "Verificando dependências..." -ForegroundColor Yellow

# Check if requirements are installed
try {
    python -c "import fastapi, uvicorn, numpy, matplotlib, skfuzzy" 2>$null
    Write-Host "✓ Dependências já instaladas" -ForegroundColor Green
} catch {
    Write-Host "Instalando dependências necessárias..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Erro na instalação das dependências" -ForegroundColor Red
        Read-Host "Pressione Enter para sair"
        exit 1
    }
    Write-Host "✓ Dependências instaladas com sucesso!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Escolha uma opção:" -ForegroundColor Cyan
Write-Host "1. Testar apenas o controlador fuzzy" -ForegroundColor White
Write-Host "2. Executar interface web completa" -ForegroundColor White
Write-Host "3. Executar teste do controlador simples" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Digite sua escolha (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Executando teste do controlador fuzzy..." -ForegroundColor Green
        Write-Host ""
        python test_elevator.py
        Read-Host "Pressione Enter para continuar"
    }
    "2" {
        Write-Host ""
        Write-Host "Iniciando servidor web..." -ForegroundColor Green
        Write-Host "Acesse: http://localhost:8000" -ForegroundColor Yellow
        Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
        Write-Host ""
        python main.py
    }
    "3" {
        Write-Host ""
        Write-Host "Executando teste do controlador simples..." -ForegroundColor Green
        Write-Host ""
        python simple_elevator_controller.py
        Read-Host "Pressione Enter para continuar"
    }
    default {
        Write-Host "Opção inválida. Executando interface web por padrão..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Iniciando servidor web..." -ForegroundColor Green
        Write-Host "Acesse: http://localhost:8000" -ForegroundColor Yellow
        Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
        Write-Host ""
        python main.py
    }
}

Write-Host ""
Write-Host "Sistema finalizado." -ForegroundColor Cyan
Read-Host "Pressione Enter para sair"
