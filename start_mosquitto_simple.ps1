# Script simples para iniciar Mosquitto
# Configuração mínima para funcionar

Write-Host "Iniciando Mosquitto MQTT Broker..." -ForegroundColor Green
Write-Host "Porta: 1883 | Host: localhost" -ForegroundColor Yellow
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Red
Write-Host ""

# Tentar diferentes configurações até uma funcionar
$mosquittoPath = "C:\Program Files\mosquitto\mosquitto.exe"

# Configuração 1: Com arquivo de config
Write-Host "Tentando com arquivo de configuração..." -ForegroundColor Yellow
try {
    & $mosquittoPath -c "mosquitto.conf" -v
} catch {
    Write-Host "Falhou com config. Tentando configuração básica..." -ForegroundColor Yellow
    
    # Configuração 2: Apenas com porta
    try {
        & $mosquittoPath -p 1883 -v
    } catch {
        Write-Host "Falhou configuração básica. Tentando padrão..." -ForegroundColor Yellow
        
        # Configuração 3: Totalmente padrão
        try {
            & $mosquittoPath -v
        } catch {
            Write-Host "✗ Erro: Não foi possível iniciar Mosquitto" -ForegroundColor Red
            Write-Host "Motivo: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}
