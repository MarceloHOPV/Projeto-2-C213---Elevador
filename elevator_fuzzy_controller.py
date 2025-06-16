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
        self.k1_down = -1.0  # adjustment constant for downward movement        
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
        """Calculate the position of each floor in meters"""
        positions = {}
        positions['subsolo'] = 0
        positions['terreo'] = 4
        
        for i in range(1, 9):
            positions[f'andar_{i}'] = 4 + (i * 3)  # terreo + floor_height * floor_number
            
        positions['tecnico'] = 4 + (8 * 3) + 4  # 32m
        
        return positions
    
    def _setup_fuzzy_system(self):
        """Setup the fuzzy control system with membership functions and rules"""
        
        # Define input and output variables
        # Error range: considering maximum building height displacement
        self.error = ctrl.Antecedent(np.arange(-36, 37, 1), 'error')
        
        # Delta error range: rate of change of error
        self.delta_error = ctrl.Antecedent(np.arange(-10, 11, 1), 'delta_error')
          # Motor power output: 0-100%
        self.motor_power = ctrl.Consequent(np.arange(0, 101, 1), 'motor_power')
        
        # Define membership functions for error (values near k2=0.212312 for better control)
        self.error['negative_large'] = fuzz.trimf(self.error.universe, [-36, -12, -1])
        self.error['negative_medium'] = fuzz.trimf(self.error.universe, [-3, -0.8, -0.2])
        self.error['negative_small'] = fuzz.trimf(self.error.universe, [-0.5, -0.21, -0.05])
        self.error['zero'] = fuzz.trimf(self.error.universe, [-0.1, 0, 0.1])
        self.error['positive_small'] = fuzz.trimf(self.error.universe, [0.05, 0.21, 0.5])
        self.error['positive_medium'] = fuzz.trimf(self.error.universe, [0.2, 0.8, 3])
        self.error['positive_large'] = fuzz.trimf(self.error.universe, [1, 12, 36])
        
        # Define membership functions for delta error (scaled proportionally to k2)
        self.delta_error['negative_large'] = fuzz.trimf(self.delta_error.universe, [-10, -3, -0.5])
        self.delta_error['negative_small'] = fuzz.trimf(self.delta_error.universe, [-1, -0.21, -0.05])
        self.delta_error['zero'] = fuzz.trimf(self.delta_error.universe, [-0.1, 0, 0.1])
        self.delta_error['positive_small'] = fuzz.trimf(self.delta_error.universe, [0.05, 0.21, 1])
        self.delta_error['positive_large'] = fuzz.trimf(self.delta_error.universe, [0.5, 3, 10])
          # Define membership functions for motor power (more aggressive for precision)
        self.motor_power['very_low'] = fuzz.trimf(self.motor_power.universe, [0, 2, 8])
        self.motor_power['low'] = fuzz.trimf(self.motor_power.universe, [5, 15, 30])
        self.motor_power['medium'] = fuzz.trimf(self.motor_power.universe, [25, 45, 65])
        self.motor_power['high'] = fuzz.trimf(self.motor_power.universe, [60, 75, 85])
        self.motor_power['very_high'] = fuzz.trimf(self.motor_power.universe, [80, 88, 90])
        
        # Define fuzzy rules for PD control
        self._setup_fuzzy_rules()
        
        # Create control system
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)
    
    def _setup_fuzzy_rules(self):
        """Define the fuzzy rules for the PD controller with smooth transitions"""
        self.rules = []
        
        # Rules for positive error (need to go up) - with smooth transitions
        self.rules.append(ctrl.Rule(self.error['positive_large'] & self.delta_error['positive_large'], self.motor_power['very_high']))
        self.rules.append(ctrl.Rule(self.error['positive_large'] & self.delta_error['positive_small'], self.motor_power['high']))
        self.rules.append(ctrl.Rule(self.error['positive_large'] & self.delta_error['zero'], self.motor_power['high']))
        self.rules.append(ctrl.Rule(self.error['positive_large'] & self.delta_error['negative_small'], self.motor_power['medium']))
        self.rules.append(ctrl.Rule(self.error['positive_large'] & self.delta_error['negative_large'], self.motor_power['medium']))  # Changed from low to medium
        
        self.rules.append(ctrl.Rule(self.error['positive_medium'] & self.delta_error['positive_large'], self.motor_power['high']))
        self.rules.append(ctrl.Rule(self.error['positive_medium'] & self.delta_error['positive_small'], self.motor_power['medium']))
        self.rules.append(ctrl.Rule(self.error['positive_medium'] & self.delta_error['zero'], self.motor_power['medium']))
        self.rules.append(ctrl.Rule(self.error['positive_medium'] & self.delta_error['negative_small'], self.motor_power['low']))
        self.rules.append(ctrl.Rule(self.error['positive_medium'] & self.delta_error['negative_large'], self.motor_power['low']))  # Changed from very_low to low
        
        self.rules.append(ctrl.Rule(self.error['positive_small'] & self.delta_error['positive_large'], self.motor_power['medium']))
        self.rules.append(ctrl.Rule(self.error['positive_small'] & self.delta_error['positive_small'], self.motor_power['low']))
        self.rules.append(ctrl.Rule(self.error['positive_small'] & self.delta_error['zero'], self.motor_power['low']))
        self.rules.append(ctrl.Rule(self.error['positive_small'] & self.delta_error['negative_small'], self.motor_power['very_low']))
        self.rules.append(ctrl.Rule(self.error['positive_small'] & self.delta_error['negative_large'], self.motor_power['very_low']))
        
        # Rules for negative error (need to go down) - with smooth transitions
        self.rules.append(ctrl.Rule(self.error['negative_large'] & self.delta_error['negative_large'], self.motor_power['very_high']))
        self.rules.append(ctrl.Rule(self.error['negative_large'] & self.delta_error['negative_small'], self.motor_power['high']))
        self.rules.append(ctrl.Rule(self.error['negative_large'] & self.delta_error['zero'], self.motor_power['high']))
        self.rules.append(ctrl.Rule(self.error['negative_large'] & self.delta_error['positive_small'], self.motor_power['medium']))
        self.rules.append(ctrl.Rule(self.error['negative_large'] & self.delta_error['positive_large'], self.motor_power['medium']))  # Changed from low to medium
        
        self.rules.append(ctrl.Rule(self.error['negative_medium'] & self.delta_error['negative_large'], self.motor_power['high']))
        self.rules.append(ctrl.Rule(self.error['negative_medium'] & self.delta_error['negative_small'], self.motor_power['medium']))
        self.rules.append(ctrl.Rule(self.error['negative_medium'] & self.delta_error['zero'], self.motor_power['medium']))
        self.rules.append(ctrl.Rule(self.error['negative_medium'] & self.delta_error['positive_small'], self.motor_power['low']))
        self.rules.append(ctrl.Rule(self.error['negative_medium'] & self.delta_error['positive_large'], self.motor_power['low']))  # Changed from very_low to low
        
        self.rules.append(ctrl.Rule(self.error['negative_small'] & self.delta_error['negative_large'], self.motor_power['medium']))
        self.rules.append(ctrl.Rule(self.error['negative_small'] & self.delta_error['negative_small'], self.motor_power['low']))
        self.rules.append(ctrl.Rule(self.error['negative_small'] & self.delta_error['zero'], self.motor_power['low']))
        self.rules.append(ctrl.Rule(self.error['negative_small'] & self.delta_error['positive_small'], self.motor_power['very_low']))
        self.rules.append(ctrl.Rule(self.error['negative_small'] & self.delta_error['positive_large'], self.motor_power['very_low']))
        
        # Rules for zero error - smooth and gentle
        self.rules.append(ctrl.Rule(self.error['zero'] & self.delta_error['negative_large'], self.motor_power['low']))
        self.rules.append(ctrl.Rule(self.error['zero'] & self.delta_error['negative_small'], self.motor_power['very_low']))
        self.rules.append(ctrl.Rule(self.error['zero'] & self.delta_error['zero'], self.motor_power['very_low']))
        self.rules.append(ctrl.Rule(self.error['zero'] & self.delta_error['positive_small'], self.motor_power['very_low']))
        self.rules.append(ctrl.Rule(self.error['zero'] & self.delta_error['positive_large'], self.motor_power['low']))
    
    def get_floor_position(self, floor_name: str) -> float:
        """Get the position of a specific floor"""
        if floor_name in self.floor_positions:
            return self.floor_positions[floor_name]
        elif floor_name.startswith('andar_'):
            return self.floor_positions[floor_name]
        else:
            raise ValueError(f"Unknown floor: {floor_name}")
    
    def compute_startup_power(self, elapsed_time: float, direction: int) -> float:
        """
        Compute motor power during the linear acceleration startup phase
        
        Args:
            elapsed_time: Time elapsed since movement started (seconds)
            direction: Movement direction (1 for up, -1 for down)
            
        Returns:
            Motor power percentage during startup (0 to 31.5%)
        """
        if elapsed_time >= self.startup_duration:
            return None  # Startup phase completed
        
        # Linear ramp: 0% → 31.5% over 2 seconds
        # P(t) = (31.5% / 2s) * t = 15.75 * t
        startup_power = (self.startup_max_power / self.startup_duration) * elapsed_time
        
        # Apply direction (positive for up, negative for down)
        return startup_power * direction
    
    def compute_control(self, current_position: float, target_position: float, previous_error: float) -> Tuple[float, float]:
        """
        Compute the fuzzy control output
        
        Args:
            current_position: Current elevator position in meters
            target_position: Target elevator position in meters
            previous_error: Previous error value for delta calculation
            
        Returns:
            Tuple of (motor_power_percentage, current_error)
        """
        # Calculate error and delta error
        current_error = target_position - current_position
        delta_error = current_error - previous_error
        
        # Set inputs to the fuzzy system
        self.simulation.input['error'] = current_error
        self.simulation.input['delta_error'] = delta_error
        
        # Compute the result
        self.simulation.compute()
        
        # Get the motor power output
        motor_power = self.simulation.output['motor_power']
        
        return motor_power, current_error
    
    def update_position(self, current_position: float, motor_power_percent: float, direction: int) -> float:
        """
        Update elevator position based on motor power using the discrete recursion model
        
        Args:
            current_position: Current position in meters
            motor_power_percent: Motor power as percentage (0-100)
            direction: 1 for up, -1 for down
            
        Returns:
            New position in meters
        """
        # Convert percentage to fraction
        motor_power_fraction = motor_power_percent / 100.0
        
        # Apply the discrete recursion model from the specification (corrected)
        # For proper movement, we need to consider direction in the position update
        position_increment = direction * motor_power_fraction * self.k2
        new_position = current_position * self.decay_factor + position_increment
        
        return new_position
    
    def simulate_movement(self, start_floor: str, target_floor: str, max_time: float = 60.0) -> dict:
        """
        Simulate elevator movement from start floor to target floor
        
        Args:
            start_floor: Starting floor name
            target_floor: Target floor name
            max_time: Maximum simulation time in seconds
            
        Returns:
            Dictionary with simulation results
        """
        start_position = self.get_floor_position(start_floor)
        target_position = self.get_floor_position(target_floor)
        
        # Determine movement direction
        direction = 1 if target_position > start_position else -1
        
        # Initialize simulation variables
        current_position = start_position
        previous_error = target_position - start_position
        
        # Data collection lists
        time_data = []
        position_data = []
        error_data = []
        motor_power_data = []        # Simulation loop
        simulation_time = 0.0
        tolerance = 0.01  # 1cm tolerance for excellent precision under 4cm target
        
        while simulation_time <= max_time:
            # Compute fuzzy control
            motor_power, current_error = self.compute_control(current_position, target_position, previous_error)
            
            # Check stopping condition
            if abs(current_error) <= tolerance:
                break
            
            # Update position
            current_position = self.update_position(current_position, motor_power, direction)
            
            # Store data
            time_data.append(simulation_time)
            position_data.append(current_position)
            error_data.append(current_error)
            motor_power_data.append(motor_power)
            
            # Update for next iteration
            previous_error = current_error
            simulation_time += self.sampling_time
        
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
        """Plot the membership functions for visualization"""
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
    controller = ElevatorFuzzyController()
    
    # Test simulation - movement from ground floor to 2nd floor
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
    
    plt.subplot(2, 2, 4)
    # Floor layout visualization
    floors = ['Subsolo', 'Terreo', 'Andar 1', 'Andar 2', 'Andar 3', 'Andar 4', 'Andar 5', 'Andar 6', 'Andar 7', 'Andar 8', 'Técnico']
    positions = [0, 4, 7, 10, 13, 16, 19, 22, 25, 28, 32]
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
