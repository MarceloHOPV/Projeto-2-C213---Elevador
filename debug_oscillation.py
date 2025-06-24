#!/usr/bin/env python3
"""
Debug detalhado da oscilação da potência
"""

from elevator_fuzzy_controller import ElevatorFuzzyController
import numpy as np
import matplotlib.pyplot as plt

def debug_oscillation():
    controller = ElevatorFuzzyController()
    
    print("🔍 Debug detalhado da oscilação...")
    result = controller.simulate_movement('terreo', 'andar_2', max_time=20.0)
    
    # Dados da simulação
    time_data = result['time']
    position_data = result['position']
    error_data = result['error']
    motor_power_data = result['motor_power']
    
    print(f"Simulação: Térreo → Andar 2")
    print(f"Tempo total: {result['final_time']:.1f}s")
    print(f"Erro final: {result['final_error_mm']:.1f}mm")
    print(f"Número de pontos: {len(time_data)}")
    
    # Análise da potência na segunda metade
    mid_point = len(motor_power_data) // 2
    late_power = motor_power_data[mid_point:]
    late_time = time_data[mid_point:]
    late_error = error_data[mid_point:]
    
    print(f"\nAnálise da segunda metade (t > {late_time[0]:.1f}s):")
    print(f"Potência média: {np.mean(late_power):.2f}%")
    print(f"Desvio padrão: {np.std(late_power):.2f}%")
    print(f"Min/Max: {min(late_power):.1f}% / {max(late_power):.1f}%")
    print(f"Variação: {max(late_power) - min(late_power):.1f}%")
    
    # Detecta mudanças bruscas na potência
    power_changes = []
    for i in range(1, len(motor_power_data)):
        change = abs(motor_power_data[i] - motor_power_data[i-1])
        if change > 5:  # Mudança maior que 5%
            power_changes.append((time_data[i], change, motor_power_data[i-1], motor_power_data[i]))
    
    print(f"\nMudanças bruscas na potência (>5%):")
    for t, change, prev, curr in power_changes[-10:]:  # Últimas 10
        print(f"t={t:.2f}s: {prev:.1f}% → {curr:.1f}% (Δ={change:.1f}%)")
    
    # Criar gráfico
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
    
    # Posição vs tempo
    ax1.plot(time_data, position_data, 'b-', linewidth=2, label='Posição')
    ax1.axhline(y=7.0, color='r', linestyle='--', alpha=0.7, label='Alvo (7m)')
    ax1.set_ylabel('Posição (m)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Movimento do Elevador: Térreo → Andar 2')
    
    # Erro vs tempo
    ax2.plot(time_data, error_data, 'g-', linewidth=2, label='Erro')
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.7)
    ax2.set_ylabel('Erro (m)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Potência vs tempo
    ax3.plot(time_data, motor_power_data, 'r-', linewidth=2, label='Potência do Motor')
    ax3.set_ylabel('Potência (%)')
    ax3.set_xlabel('Tempo (s)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Destaca a segunda metade
    ax3.axvline(x=late_time[0], color='orange', linestyle='--', alpha=0.7, label='Segunda metade')
    
    plt.tight_layout()
    plt.savefig('debug_oscillation.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"\nGráfico salvo em: debug_oscillation.png")

if __name__ == "__main__":
    debug_oscillation()
