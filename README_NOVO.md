# Sistema de Controle Fuzzy para Elevador VILLARTA COMPAQ Slim

Sistema de controle inteligente baseado em lógica fuzzy para elevador de 11 andares com especificações VILLARTA COMPAQ Slim.

## 📋 Arquivos Principais

- `main.py` - Servidor web principal (FastAPI + WebSocket)
- `elevator_fuzzy_controller.py` - Controlador fuzzy principal
- `simple_elevator_controller.py` - Controlador simplificado para testes
- `teste_oficial.py` - **Arquivo de teste oficial padronizado**
- `templates/index.html` - Interface web do sistema
- `static/style.css` - Estilos da interface

## 🚀 Como Executar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar Interface Web
```bash
python main.py
```
Acesse: http://localhost:8000

### 3. **Executar Teste Oficial** (RECOMENDADO)
```bash
python teste_oficial.py
```

## 🧪 Teste Oficial

O arquivo `teste_oficial.py` executa uma bateria completa de testes padronizados:

### Cenários Testados:
1. **Térreo → 1º Andar** (movimento curto - subida)
2. **1º Andar → Térreo** (movimento curto - descida)  
3. **Térreo → 4º Andar** (movimento médio - subida)
4. **4º Andar → Térreo** (movimento médio - descida)
5. **Térreo → 8º Andar** (movimento longo - subida)
6. **8º Andar → Térreo** (movimento longo - descida)

### Métricas Coletadas:
- ⏱️ **Tempo total** de movimento
- 📏 **Erro final** em milímetros
- ⚡ **Potência máxima** atingida (0-100%)
- 📊 **Taxa de sucesso** (erro < 5cm)

### Saída do Teste:
- Relatório detalhado no console
- Arquivo JSON com resultados (`resultados_teste_oficial_YYYYMMDD_HHMMSS.json`)
- Estatísticas completas de desempenho

## 🏗️ Especificações Técnicas

### Elevador VILLARTA COMPAQ Slim:
- **Altura total**: 36 metros
- **Andares**: 11 (Subsolo + Térreo + Andares 1-8 + Técnico)
- **Capacidade**: 975kg (13 passageiros)
- **Velocidade máxima**: 1.0 m/s

### Sistema de Controle:
- **Controle Fuzzy PD** com 5 níveis de erro e potência
- **Sistema de Aceleração Linear** (primeiros 2 segundos)
- **Fallback proporcional** para casos de falha do fuzzy
- **Precisão**: <5cm de erro final
- **Amostragem**: 200ms (5Hz)

## 📊 Critérios de Aprovação

O sistema é considerado **APROVADO** se:
- ✅ Taxa de sucesso ≥ 80% nos 6 cenários
- ✅ Erro final < 50mm em cada teste
- ✅ Potência máxima entre 80-95% para movimentos longos
- ✅ Tempo de movimento adequado (sem travamentos)

## 🛠️ Desenvolvimento

### Arquitetura:
- **Backend**: FastAPI + WebSocket para comunicação em tempo real
- **Frontend**: HTML/JS com gráficos Plotly para visualização
- **Controle**: Scikit-fuzzy para lógica fuzzy + modelo discreto de posição

### Principais Melhorias Implementadas:
- 🔧 Correção da lógica de sinal da potência
- 🔧 Melhoria na transição startup→fuzzy
- 🔧 Controle robusto de overshoot
- 🔧 Fallback inteligente para falhas do fuzzy
- 🔧 Interface visual clara com direção separada da potência

---
**Versão**: 2.0 - Sistema Otimizado e Testado
**Data**: Dezembro 2024
