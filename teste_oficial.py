"""
TESTE OFICIAL - Sistema de Controle Fuzzy para Elevador
Cenários de teste padronizados para validação do sistema

Testa os seguintes movimentos:
1. Térreo → 1º Andar
2. 1º Andar → Térreo  
3. Térreo → 4º Andar
4. 4º Andar → Térreo
5. Térreo → 8º Andar
6. 8º Andar → Térreo

Autor: Sistema de Controle Fuzzy VILLARTA COMPAQ Slim
"""

import time
import asyncio
from simple_elevator_controller import SimpleElevatorController
import json

class TesteOficial:
    def __init__(self):
        self.controller = SimpleElevatorController()
        self.resultados = []
        self.teste_atual = 0
        
        # Cenários de teste oficiais
        self.cenarios = [
            {"nome": "Térreo → 1º Andar", "origem": "terreo", "destino": "andar_1"},
            {"nome": "1º Andar → Térreo", "origem": "andar_1", "destino": "terreo"},
            {"nome": "Térreo → 4º Andar", "origem": "terreo", "destino": "andar_4"},
            {"nome": "4º Andar → Térreo", "origem": "andar_4", "destino": "terreo"},
            {"nome": "Térreo → 8º Andar", "origem": "terreo", "destino": "andar_8"},
            {"nome": "8º Andar → Térreo", "origem": "andar_8", "destino": "terreo"},
        ]
        
        # Configurar callbacks
        self.controller.set_position_callback(self._callback_posicao)
        self.controller.set_status_callback(self._callback_status)
        
        # Dados para coleta de métricas
        self.dados_movimento = []
        self.tempo_inicio = None
        self.potencia_maxima = 0
        self.erro_final = 0
        
    def _callback_posicao(self, data):
        """Callback para atualizações de posição durante o movimento"""
        if self.tempo_inicio:
            tempo_decorrido = data['timestamp'] - self.tempo_inicio
            self.dados_movimento.append({
                'tempo': tempo_decorrido,
                'posicao': data['current_position'],
                'potencia': abs(data['motor_power']),  # Sempre positiva conforme projeto
                'erro': abs(data['error']),
                'direcao': data['direction']
            })
            
            # Atualizar potência máxima
            potencia_abs = abs(data['motor_power'])
            if potencia_abs > self.potencia_maxima:
                self.potencia_maxima = potencia_abs
                
            # Imprimir progresso a cada 2 segundos
            if len(self.dados_movimento) % 10 == 0:
                print(f"  Tempo: {tempo_decorrido:.1f}s | Posição: {data['current_position']:.2f}m | "
                      f"Potência: {potencia_abs:.1f}% | Erro: {abs(data['error'])*1000:.1f}mm")
    
    def _callback_status(self, data):
        """Callback para atualizações de status"""
        if not data['is_moving'] and self.tempo_inicio:
            # Movimento concluído
            tempo_total = time.time() - self.tempo_inicio
            self.erro_final = abs(self.controller.target_position - self.controller.current_position)
            
            print(f"  ✅ Movimento concluído em {tempo_total:.1f}s")
            print(f"  📍 Erro final: {self.erro_final*1000:.1f}mm")
            print(f"  ⚡ Potência máxima: {self.potencia_maxima:.1f}%")
    
    def _posicionar_elevador(self, andar_inicial):
        """Posiciona o elevador no andar inicial sem contar como teste"""
        if self.controller.current_floor != andar_inicial:
            print(f"📍 Posicionando elevador no {andar_inicial}...")
            self.controller.current_floor = andar_inicial
            self.controller.current_position = self.controller.controller.get_floor_position(andar_inicial)
            print(f"   Elevador posicionado em {self.controller.current_position:.2f}m")
    
    def _executar_cenario(self, cenario):
        """Executa um cenário de teste específico"""
        print(f"\n{'='*60}")
        print(f"🧪 TESTE {self.teste_atual + 1}/6: {cenario['nome']}")
        print(f"{'='*60}")
        
        # Posicionar elevador no andar inicial
        self._posicionar_elevador(cenario['origem'])
        
        # Resetar dados de coleta
        self.dados_movimento = []
        self.potencia_maxima = 0
        self.erro_final = 0
        self.tempo_inicio = time.time()
        
        # Iniciar movimento
        origem_pos = self.controller.controller.get_floor_position(cenario['origem'])
        destino_pos = self.controller.controller.get_floor_position(cenario['destino'])
        distancia = abs(destino_pos - origem_pos)
        direcao = "Subida" if destino_pos > origem_pos else "Descida"
        
        print(f"🎯 Origem: {cenario['origem']} ({origem_pos:.1f}m)")
        print(f"🎯 Destino: {cenario['destino']} ({destino_pos:.1f}m)")
        print(f"📏 Distância: {distancia:.1f}m | Direção: {direcao}")
        print(f"⏱️  Iniciando movimento...")
        
        # Executar movimento
        sucesso = self.controller.move_to_floor(cenario['destino'])
        
        if not sucesso:
            print("❌ Falha ao iniciar movimento!")
            return False
        
        # Aguardar conclusão do movimento
        timeout = 60  # 60 segundos de timeout
        tempo_inicial = time.time()
        
        while self.controller.is_moving:
            time.sleep(0.1)
            if time.time() - tempo_inicial > timeout:
                print("⏰ Timeout! Parando movimento...")
                self.controller.emergency_stop()
                break
        
        # Coletar resultados
        tempo_total = time.time() - self.tempo_inicio
        
        resultado = {
            'teste': self.teste_atual + 1,
            'cenario': cenario['nome'],
            'origem': cenario['origem'],
            'destino': cenario['destino'],
            'distancia_m': distancia,
            'direcao': direcao,
            'tempo_total_s': tempo_total,
            'erro_final_mm': self.erro_final * 1000,
            'potencia_maxima_pct': self.potencia_maxima,
            'dados_movimento': self.dados_movimento.copy(),
            'sucesso': bool(self.erro_final < 0.05)  # Erro menor que 5cm = sucesso
        }
        
        self.resultados.append(resultado)
        
        # Resumo do teste
        print(f"\n📊 RESUMO DO TESTE:")
        print(f"   ⏱️  Tempo total: {tempo_total:.1f}s")
        print(f"   📏 Erro final: {self.erro_final*1000:.1f}mm")
        print(f"   ⚡ Potência máxima: {self.potencia_maxima:.1f}%")
        print(f"   ✅ Status: {'SUCESSO' if resultado['sucesso'] else 'FALHA'}")
        
        self.teste_atual += 1
        return resultado['sucesso']
    
    def executar_todos_testes(self):
        """Executa todos os cenários de teste"""
        print("🚀 INICIANDO TESTE OFICIAL DO SISTEMA DE CONTROLE FUZZY")
        print("🏢 Elevador VILLARTA COMPAQ Slim - 11 andares")
        print(f"📋 {len(self.cenarios)} cenários de teste programados")
        
        # Conectar controlador
        self.controller.connect()
        
        sucessos = 0
        
        try:
            for cenario in self.cenarios:
                sucesso = self._executar_cenario(cenario)
                if sucesso:
                    sucessos += 1
                
                # Pausa entre testes
                if self.teste_atual < len(self.cenarios):
                    print(f"\n⏸️  Aguardando 3 segundos antes do próximo teste...")
                    time.sleep(3)
            
            # Relatório final
            self._gerar_relatorio_final(sucessos)
            
        except KeyboardInterrupt:
            print("\n🛑 Testes interrompidos pelo usuário")
        finally:
            self.controller.disconnect()
    
    def _gerar_relatorio_final(self, sucessos):
        """Gera relatório final dos testes"""
        print(f"\n{'='*80}")
        print(f"📊 RELATÓRIO FINAL - TESTE OFICIAL COMPLETO")
        print(f"{'='*80}")
        
        total_testes = len(self.cenarios)
        taxa_sucesso = (sucessos / total_testes) * 100
        
        print(f"🎯 Testes executados: {total_testes}")
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Falhas: {total_testes - sucessos}")
        print(f"📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        print(f"\n📋 RESULTADOS DETALHADOS:")
        print(f"{'Teste':<6} {'Cenário':<20} {'Tempo(s)':<9} {'Erro(mm)':<10} {'Pot.Max(%)':<11} {'Status':<8}")
        print("-" * 70)
        
        for resultado in self.resultados:
            status = "✅ OK" if resultado['sucesso'] else "❌ FALHA"
            print(f"{resultado['teste']:<6} {resultado['cenario']:<20} "
                  f"{resultado['tempo_total_s']:<9.1f} {resultado['erro_final_mm']:<10.1f} "
                  f"{resultado['potencia_maxima_pct']:<11.1f} {status:<8}")
        
        # Estatísticas
        if self.resultados:
            tempos = [r['tempo_total_s'] for r in self.resultados]
            erros = [r['erro_final_mm'] for r in self.resultados]
            potencias = [r['potencia_maxima_pct'] for r in self.resultados]
            
            print(f"\n📈 ESTATÍSTICAS:")
            print(f"   Tempo médio: {sum(tempos)/len(tempos):.1f}s")
            print(f"   Erro médio: {sum(erros)/len(erros):.1f}mm")
            print(f"   Potência média máxima: {sum(potencias)/len(potencias):.1f}%")
            print(f"   Maior potência atingida: {max(potencias):.1f}%")
        
        # Salvar resultados em arquivo
        self._salvar_resultados()
        
        print(f"\n🎉 TESTE OFICIAL CONCLUÍDO!")
        if taxa_sucesso >= 80:
            print("🏆 SISTEMA APROVADO! Taxa de sucesso ≥ 80%")
        else:
            print("⚠️  SISTEMA NECESSITA AJUSTES. Taxa de sucesso < 80%")
    
    def _salvar_resultados(self):
        """Salva os resultados em arquivo JSON"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"resultados_teste_oficial_{timestamp}.json"
        
        dados_completos = {
            'timestamp': time.time(),
            'data_teste': time.strftime("%Y-%m-%d %H:%M:%S"),
            'total_testes': len(self.cenarios),
            'sucessos': sum(1 for r in self.resultados if r['sucesso']),
            'taxa_sucesso_pct': (sum(1 for r in self.resultados if r['sucesso']) / len(self.cenarios)) * 100,
            'resultados': self.resultados
        }
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_completos, f, indent=2, ensure_ascii=False)
            print(f"💾 Resultados salvos em: {nome_arquivo}")
        except Exception as e:
            print(f"❌ Erro ao salvar resultados: {e}")

def main():
    """Função principal"""
    print("Sistema de Teste Oficial - Elevador Fuzzy Controller")
    print("Pressione Ctrl+C a qualquer momento para interromper")
    
    teste = TesteOficial()
    teste.executar_todos_testes()

if __name__ == "__main__":
    main()
