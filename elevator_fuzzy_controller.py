import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
from typing import Tuple, List
import time

class ElevatorFuzzyController:
    """
    Fuzzy PD Controller for Elevator Position and Velocity Control
    Based on the Villarta Standard COMPAQ Slim specifications
    """
    
    def __init__(self):
        # Building specifications
        self.building_height = 36  # meters
        self.floors = 11
        self.floor_heights = {
            'subsolo': 4,
            'terreo': 4, 
            'andares_1_8': 3,
            'tecnico': 4
        }
        
        # Elevator specifications
        self.max_speed = 1.0  # m/s
        self.max_capacity = 975  # kg
        self.max_passengers = 13        # Control parameters
        self.sampling_time = 0.2  # 200ms
        self.k1_up = 1.0  # adjustment constant for upward movement
        self.k1_down = -1.0  # adjustment constant for downward movement (negativo para descida)
        self.k2 = 0.251287  # power to position increment conversion factor (from PDF specification)
        self.decay_factor = 0.999  # decay factor from specification (0.999 not 0.9995)
        
        # Linear Acceleration System parameters (from PDF Figure 3)
        self.startup_duration = 2.0  # 2 seconds startup ramp
        self.startup_max_power = 31.5  # 31.5% maximum power during startup
          # Floor positions (height from ground level)
        self.floor_positions = self._calculate_floor_positions()        
        # Initialize fuzzy system
        self._setup_fuzzy_system()
        
    def _calculate_floor_positions(self) -> dict:
        """Calculate the position of each floor in meters
        
        Building specification (alturas corretas):
        - Subsolo: 4m de altura, posição 0m (referência)
        - Térreo: 4m de altura, posição 4m
        - Andar 1: 3m de altura, posição 8m (4+4)
        - Andares 2-8: 3m cada, posições 11m, 14m, 17m, 20m, 23m, 26m, 29m
        - Técnico: 4m de altura, posição 33m (29+4)
        """
        positions = {}
        positions['subsolo'] = 0        # Referência
        positions['terreo'] = 4         # 4m
        positions['andar_1'] = 8        # 4+4=8m
        positions['andar_2'] = 11       # 8+3=11m
        positions['andar_3'] = 14       # 11+3=14m
        positions['andar_4'] = 17       # 14+3=17m
        positions['andar_5'] = 20       # 17+3=20m
        positions['andar_6'] = 23       # 20+3=23m
        positions['andar_7'] = 26       # 23+3=26m
        positions['andar_8'] = 29       # 26+3=29m
        positions['tecnico'] = 32       # 29+3=32m (andar 8 tem 3m + técnico 4m)
        
        return positions
    
    def _setup_fuzzy_system(self):
        """Setup the fuzzy control system with membership functions and rules"""
          # Define input and output variables
        # Error range: considering maximum building height displacement (0 to 30m with extra margin)
        self.error = ctrl.Antecedent(np.arange(0, 31, 0.25), 'error')
        
        # Delta error range: rate of change of error
        self.delta_error = ctrl.Antecedent(np.arange(-10, 11, 0.25), 'delta_error')
        
        # Motor power output: 0-100%
        self.motor_power = ctrl.Consequent(np.arange(0, 101, 1), 'motor_power')
          # Define membership functions for error (0 to 30m range) - corrigido para cobertura completa
        self.error['very_small'] = fuzz.trimf(self.error.universe, [0, 0, 0.8])        # 0-0.8m (overlap com small)
        self.error['small'] = fuzz.trimf(self.error.universe, [0.5, 5, 12])            # overlap desde 0.5m
        self.error['medium'] = fuzz.trimf(self.error.universe, [5, 15, 20])           # ~15m center (overlap melhor)
        self.error['large'] = fuzz.trimf(self.error.universe, [15, 24, 30])            # ~24m center (overlap desde 18m)
        
        # Define membership functions for delta error (ajustado para ser menos sensível)
        self.delta_error['negative_large'] = fuzz.trimf(self.delta_error.universe, [-10, -2, -0.5])
        self.delta_error['negative_small'] = fuzz.trimf(self.delta_error.universe, [-1, -0.2, -0.05])
        self.delta_error['zero'] = fuzz.trimf(self.delta_error.universe, [-0.3, 0, 0.3])
        self.delta_error['positive_small'] = fuzz.trimf(self.delta_error.universe, [0.05, 0.2, 1])
        self.delta_error['positive_large'] = fuzz.trimf(self.delta_error.universe, [0.5, 5, 10])
        
        # Define membership functions for motor power - ajustado para acelerar movimentos curtos
        self.motor_power['low'] = fuzz.trimf(self.motor_power.universe, [10, 40, 50])       # Centro em 40% para acelerar movimentos curtos
        self.motor_power['medium'] = fuzz.trimf(self.motor_power.universe, [45, 55, 65])     # ~55% (15m)  
        self.motor_power['high'] = fuzz.trimf(self.motor_power.universe, [60, 70, 80])       # ~70% intermediário
        self.motor_power['very_high'] = fuzz.trimf(self.motor_power.universe, [75, 85, 90])  # ~85% próximo de 90%
        
        # Define fuzzy rules for PD control
        self._setup_fuzzy_rules()
        
        # Create control system
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)
    
    def _setup_fuzzy_rules(self):
        """Define the fuzzy rules for the PD controller - versão simplificada e robusta"""
        self.rules = []
        
        # Regras para erro muito pequeno (chegando ao destino)
        self.rules.append(ctrl.Rule(self.error['very_small'], self.motor_power['low']))
        
        # Regras para erro pequeno (~9m) - alvejando ~31.5%
        self.rules.append(ctrl.Rule(self.error['small'] & self.delta_error['positive_large'], self.motor_power['medium']))
        self.rules.append(ctrl.Rule(self.error['small'] & self.delta_error['positive_small'], self.motor_power['low']))
        self.rules.append(ctrl.Rule(self.error['small'] & self.delta_error['zero'], self.motor_power['low']))
        self.rules.append(ctrl.Rule(self.error['small'] & self.delta_error['negative_small'], self.motor_power['low']))
        self.rules.append(ctrl.Rule(self.error['small'] & self.delta_error['negative_large'], self.motor_power['low']))
        
        # Regras para erro médio (~15m) - alvejando ~45%
        self.rules.append(ctrl.Rule(self.error['medium'] & self.delta_error['positive_large'], self.motor_power['high']))
        self.rules.append(ctrl.Rule(self.error['medium'] & self.delta_error['positive_small'], self.motor_power['medium']))
        self.rules.append(ctrl.Rule(self.error['medium'] & self.delta_error['zero'], self.motor_power['medium']))
        self.rules.append(ctrl.Rule(self.error['medium'] & self.delta_error['negative_small'], self.motor_power['medium']))
        self.rules.append(ctrl.Rule(self.error['medium'] & self.delta_error['negative_large'], self.motor_power['low']))
        
        # Regras para erro grande (~21m) - alvejando ~85-90%
        self.rules.append(ctrl.Rule(self.error['large'] & self.delta_error['positive_large'], self.motor_power['very_high']))
        self.rules.append(ctrl.Rule(self.error['large'] & self.delta_error['positive_small'], self.motor_power['very_high']))
        self.rules.append(ctrl.Rule(self.error['large'] & self.delta_error['zero'], self.motor_power['very_high']))
        self.rules.append(ctrl.Rule(self.error['large'] & self.delta_error['negative_small'], self.motor_power['high']))
        self.rules.append(ctrl.Rule(self.error['large'] & self.delta_error['negative_large'], self.motor_power['medium']))
    
    def get_floor_position(self, floor_name: str) -> float:
        """Get the position of a specific floor"""
        if floor_name in self.floor_positions:
            return self.floor_positions[floor_name]
        elif floor_name.startswith('andar_'):
            return self.floor_positions[floor_name]
        else:
            raise ValueError(f"Unknown floor: {floor_name}")
    
    def compute_startup_power(self, elapsed_time: float, direction: int) -> float:
        if elapsed_time >= self.startup_duration:
            return None  # Startup phase completed
          # Linear ramp: 0% → 31.5% over 2 seconds
        # P(t) = (31.5% / 2s) * t = 15.75 * t
        startup_power = (self.startup_max_power / self.startup_duration) * elapsed_time
        
        # Sempre retorna potência positiva - direção é controlada pelo k1 agora
        return startup_power
    
    def compute_control(self, current_position: float, target_position: float, previous_error: float) -> Tuple[float, float]:
        # Calculate error and delta error with proper sign
        current_error = target_position - current_position  # Keep sign for direction
        error_magnitude = abs(current_error)  # Use absolute error for fuzzy input
        delta_error = error_magnitude - abs(previous_error)  # Change in error magnitude
        
        # Set inputs to the fuzzy system (ensure values are in valid range)
        error_input = max(0, min(30, error_magnitude))
        delta_input = max(-8, min(8, delta_error))  # Reduzido para evitar saturação nos extremos
        
        try:
            self.simulation.input['error'] = error_input
            self.simulation.input['delta_error'] = delta_input
            self.simulation.compute()
            # Get the motor power output - sempre positivo agora
            motor_power = self.simulation.output['motor_power']
            
        except Exception as e:
            print(f"Fuzzy computation error: {e}")
            print(f"Inputs: error={error_input}, delta_error={delta_input}")
            # Fallback simples: básico proporcional respeitando limite de 90%
            motor_power = min(90.0, max(5.0, error_magnitude * 2.5))  # Só garante que não passe de 90%
            print(f"Using fallback motor power: {motor_power}% (positive)")
        
        # Garantir que a potência nunca exceda 90%
        motor_power = min(90.0, motor_power)
        
        return motor_power, current_error
    
    def update_position(self, current_position: float, motor_power_percent: float, direction: int, elapsed_time: float = None) -> float:
        # k1 controla a direção: k1_up=+1.0 para subida, k1_down=-1.0 para descida
        k1 = self.k1_up if direction > 0 else self.k1_down
        
        # Motor power sempre positivo (conforme especificação do projeto)
        motor_power_fraction = motor_power_percent / 100.0
        
        # Two-stage model based on elapsed time (seguindo fórmula exata do professor)
        if elapsed_time is not None and elapsed_time <= 2.0:
            # First 2 seconds: posição_atual = k1 * posição_atual * 0.999 + potência_motor * 0.251287
            new_position_raw = k1 * current_position * 0.999 + motor_power_fraction * 0.251287
        else:
            # After 2 seconds: posição_atual = k1 * posição_atual * 0.9995 + potência_motor * 0.212312
            new_position_raw = k1 * current_position * 0.9995 + motor_power_fraction * 0.212312
        
        # Aplicar valor absoluto para garantir posição sempre positiva
        new_position = abs(new_position_raw)
        
        return new_position
    
    def simulate_movement(self, start_floor: str, target_floor: str, max_time: float = 80) -> dict:
        start_position = self.get_floor_position(start_floor)
        target_position = self.get_floor_position(target_floor)
        
        # Determine movement direction
        direction = 1 if target_position > start_position else -1        # Initialize simulation variables
        current_position = start_position
        previous_error = abs(target_position - start_position)  # Use absolute error# Keep sign for direction
        
        # Data collection lists
        time_data = []
        position_data = []
        error_data = []
        motor_power_data = []        # Simulation loop
        simulation_time = 0.0
        # Tolerância adaptativa baseada na distância
        distance = abs(target_position - start_position)
        if distance >= 20:  # Movimentos muito longos (>20m)
            tolerance = 0.39  # 30cm para distâncias muito longas
        elif distance >= 15:  # Movimentos longos (15-20m)
            tolerance = 0.20  # 20cm para distâncias longas
        else:  # Movimentos curtos/médios (<15m)
            tolerance = 0.10  # 10cm para distâncias normais
            
        max_iterations = int(max_time / self.sampling_time)
        iterations = 0
        
        while simulation_time <= max_time and iterations < max_iterations:
            # Compute fuzzy control
            motor_power, current_error = self.compute_control(current_position, target_position, previous_error)
              # Check stopping condition
            if abs(current_error) <= tolerance:
                break
              # Update position with elapsed time for two-stage model
            current_position = self.update_position(current_position, motor_power, direction, simulation_time)
            
            # Store data
            time_data.append(simulation_time)
            position_data.append(current_position)
            error_data.append(current_error)
            motor_power_data.append(motor_power)
              # Update for next iteration
            previous_error = abs(current_error)  # Store absolute error for next iteration
            simulation_time += self.sampling_time
            iterations += 1
        
        # Calculate performance metrics
        final_error = abs(target_position - current_position) * 1000  # in mm
        peak_position = max(position_data) if direction > 0 else min(position_data)
        overshoot = abs(peak_position - target_position)
        overshoot_percent = (overshoot / abs(target_position - start_position)) * 100 if abs(target_position - start_position) > 0 else 0
        
        return {
            'time': time_data,
            'position': position_data,
            'error': error_data,
            'motor_power': motor_power_data,
            'final_time': simulation_time,
            'final_error_mm': final_error,
            'peak_position': peak_position,
            'overshoot_percent': overshoot_percent,
            'start_position': start_position,
            'target_position': target_position,
            'direction': 'Subida' if direction > 0 else 'Descida'
        }
    
    def plot_membership_functions(self):
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
        
        # Plot error membership functions
        self.error.view(ax=ax1)
        ax1.set_title('Error Membership Functions')
        ax1.set_xlabel('Error (m)')
        
        # Plot delta error membership functions  
        self.delta_error.view(ax=ax2)
        ax2.set_title('Delta Error Membership Functions')
        ax2.set_xlabel('Delta Error (m/s)')
        
        # Plot motor power membership functions
        self.motor_power.view(ax=ax3)
        ax3.set_title('Motor Power Membership Functions')
        ax3.set_xlabel('Motor Power (%)')
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # Create elevator controller
    controller = ElevatorFuzzyController()    # Test simulation - movement from ground floor to 2nd floor
    print("Testing elevator movement from Terreo to Andar 2...")
    result = controller.simulate_movement('terreo', 'andar_2')
    
    print(f"Simulation completed in {result['final_time']:.1f} seconds")
    print(f"Final error: {result['final_error_mm']:.1f} mm")
    print(f"Overshoot: {result['overshoot_percent']:.4f}%")
    print(f"Direction: {result['direction']}")
      # Plot results
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.plot(result['time'], result['position'])
    plt.axhline(y=result['target_position'], color='r', linestyle='--', label='Target')
    plt.title('Elevator Position vs Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Position (m)')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(2, 2, 2)
    plt.plot(result['time'], result['error'])
    plt.title('Position Error vs Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Error (m)')
    plt.grid(True)
    
    plt.subplot(2, 2, 3)
    plt.plot(result['time'], result['motor_power'])
    plt.title('Motor Power vs Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Motor Power (%)')
    plt.grid(True)
    
    plt.subplot(2, 2, 4)    # Floor layout visualization
    floors = ['Subsolo', 'Terreo', 'Andar 1', 'Andar 2', 'Andar 3', 'Andar 4', 'Andar 5', 'Andar 6', 'Andar 7', 'Andar 8', 'Técnico']
    positions = [0, 4, 8, 11, 14, 17, 20, 23, 26, 29, 32]  # Corrected positions: técnico = 32m
    plt.barh(range(len(floors)), positions, alpha=0.3)
    plt.axvline(x=result['target_position'], color='r', linestyle='--', label='Target Floor')
    plt.axvline(x=result['position'][-1], color='g', linestyle='-', label='Final Position')
    plt.yticks(range(len(floors)), floors)
    plt.xlabel('Position (m)')
    plt.title('Building Layout')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
