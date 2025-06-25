"""
Elevator Fuzzy Controller - Performance Analysis Plotter
Plots motor power, delta error, and error graphics for analysis

Usage:
    python plot_analysis.py
    
Features:
- Real-time simulation plotting
- Multiple scenarios comparison
- Error and delta error analysis
- Motor power behavior visualization
"""

import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from elevator_fuzzy_controller import ElevatorFuzzyController
import time

class ElevatorPlotter:
    def __init__(self):
        self.controller = ElevatorFuzzyController()
        self.scenarios = [
            {"name": "Short Up", "start": "terreo", "end": "andar_1", "color": "blue"},
            {"name": "Medium Up", "start": "terreo", "end": "andar_4", "color": "green"},
            {"name": "Long Up", "start": "terreo", "end": "andar_8", "color": "red"},
            {"name": "Short Down", "start": "andar_1", "end": "terreo", "color": "cyan"},
            {"name": "Medium Down", "start": "andar_4", "end": "terreo", "color": "orange"},
            {"name": "Long Down", "start": "andar_8", "end": "terreo", "color": "purple"}
        ]
    
    def simulate_scenario(self, start_floor, end_floor):
        """Simulate movement and collect data"""
        print(f"🔄 Simulating {start_floor} → {end_floor}...")
        
        start_pos = self.controller.get_floor_position(start_floor)
        end_pos = self.controller.get_floor_position(end_floor)
        direction = 1 if end_pos > start_pos else -1
        
        # Data storage
        time_data = []
        position_data = []
        error_data = []
        delta_error_data = []
        motor_power_data = []
        
        # Simulation parameters
        current_pos = start_pos
        previous_error = abs(end_pos - start_pos)
        elapsed_time = 0.0
        tolerance = 0.02  # 2cm
        max_time = 60.0
        
        while elapsed_time <= max_time:
            current_error = end_pos - current_pos
            error_magnitude = abs(current_error)
            
            # Stop condition
            if error_magnitude <= tolerance:
                break
            
            # Calculate delta error
            delta_error = error_magnitude - previous_error
            
            # Get motor power from fuzzy controller
            motor_power, _ = self.controller.compute_control(
                current_pos, end_pos, previous_error
            )
            
            # Handle startup phase
            if elapsed_time <= 2.0:
                startup_power = self.controller.compute_startup_power(elapsed_time, direction)
                if startup_power is not None:
                    motor_power = startup_power
            
            # Update position
            current_pos = self.controller.update_position(
                current_pos, abs(motor_power), direction, elapsed_time
            )
            
            # Store data
            time_data.append(elapsed_time)
            position_data.append(current_pos)
            error_data.append(current_error)
            delta_error_data.append(delta_error)
            motor_power_data.append(motor_power)
            
            # Update for next iteration
            previous_error = error_magnitude
            elapsed_time += self.controller.sampling_time
        
        return {
            'time': time_data,
            'position': position_data,
            'error': error_data,
            'delta_error': delta_error_data,
            'motor_power': motor_power_data,
            'start_floor': start_floor,
            'end_floor': end_floor,
            'direction': 'Up' if direction > 0 else 'Down'
        }
    
    def plot_single_scenario(self, scenario_data):
        """Plot a single scenario with 4 subplots"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f"Elevator Analysis: {scenario_data['start_floor']} → {scenario_data['end_floor']} ({scenario_data['direction']})", 
                     fontsize=16, fontweight='bold')
        
        time_data = scenario_data['time']
        
        # 1. Position vs Time
        ax1.plot(time_data, scenario_data['position'], 'b-', linewidth=2, label='Position')
        ax1.axhline(y=self.controller.get_floor_position(scenario_data['end_floor']), 
                   color='r', linestyle='--', alpha=0.7, label='Target')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Position (m)')
        ax1.set_title('Position vs Time')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # 2. Error vs Time
        ax2.plot(time_data, scenario_data['error'], 'g-', linewidth=2, label='Position Error')
        ax2.axhline(y=0, color='r', linestyle='--', alpha=0.7, label='Target (0 error)')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Error (m)')
        ax2.set_title('Position Error vs Time')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # 3. Delta Error vs Time
        ax3.plot(time_data, scenario_data['delta_error'], 'orange', linewidth=2, label='Delta Error')
        ax3.axhline(y=0, color='r', linestyle='--', alpha=0.7, label='Zero change')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Delta Error (m)')
        ax3.set_title('Delta Error vs Time')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # 4. Motor Power vs Time
        ax4.plot(time_data, [abs(p) for p in scenario_data['motor_power']], 'purple', linewidth=2, label='Motor Power')
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Motor Power (%)')
        ax4.set_title('Motor Power vs Time')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        ax4.set_ylim(0, 100)
        
        plt.tight_layout()
        return fig
    
    def plot_comparison(self, scenarios_data):
        """Plot comparison of multiple scenarios"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Elevator Performance Comparison - All Scenarios', fontsize=16, fontweight='bold')
        
        colors = ['blue', 'green', 'red', 'cyan', 'orange', 'purple']
        
        for i, (scenario, color) in enumerate(zip(scenarios_data, colors)):
            label = f"{scenario['start_floor']} → {scenario['end_floor']}"
            time_data = scenario['time']
            
            # Normalize time for comparison (optional)
            max_time = max(time_data) if time_data else 1
            norm_time = [t/max_time for t in time_data]
            
            # 1. Position trajectories
            ax1.plot(time_data, scenario['position'], color=color, linewidth=2, label=label, alpha=0.8)
            
            # 2. Error evolution
            ax2.plot(time_data, [abs(e) for e in scenario['error']], color=color, linewidth=2, label=label, alpha=0.8)
            
            # 3. Delta error patterns
            ax3.plot(time_data, scenario['delta_error'], color=color, linewidth=2, label=label, alpha=0.8)
            
            # 4. Motor power usage
            ax4.plot(time_data, [abs(p) for p in scenario['motor_power']], color=color, linewidth=2, label=label, alpha=0.8)
        
        # Configure subplots
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Position (m)')
        ax1.set_title('Position Trajectories')
        ax1.grid(True, alpha=0.3)
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('|Error| (m)')
        ax2.set_title('Error Magnitude')
        ax2.grid(True, alpha=0.3)
        ax2.set_yscale('log')  # Log scale for better error visualization
        
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Delta Error (m)')
        ax3.set_title('Delta Error Patterns')
        ax3.grid(True, alpha=0.3)
        ax3.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Motor Power (%)')
        ax4.set_title('Motor Power Usage')
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 100)
        
        plt.tight_layout()
        return fig
    
    def plot_fuzzy_surfaces(self):
        """Plot fuzzy system membership functions and control surface"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Fuzzy Controller Analysis', fontsize=16, fontweight='bold')
          # 1. Error membership functions
        error_levels = ['very_small', 'small', 'medium', 'large']
        colors = ['blue', 'green', 'orange', 'red']
        
        for i, level in enumerate(error_levels):
            membership_values = self.controller.error[level].mf
            ax1.plot(self.controller.error.universe, membership_values, 
                    label=level.replace('_', ' ').title(), color=colors[i], linewidth=2)
        ax1.set_xlabel('Error (m)')
        ax1.set_ylabel('Membership')
        ax1.set_title('Error Membership Functions')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
          # 2. Delta error membership functions
        delta_levels = ['negative_large', 'negative_small', 'zero', 'positive_small', 'positive_large']
        delta_colors = ['red', 'orange', 'blue', 'green', 'purple']
        
        for i, level in enumerate(delta_levels):
            membership_values = self.controller.delta_error[level].mf
            ax2.plot(self.controller.delta_error.universe, membership_values, 
                    label=level.replace('_', ' ').title(), color=delta_colors[i], linewidth=2)
        ax2.set_xlabel('Delta Error (m)')
        ax2.set_ylabel('Membership')
        ax2.set_title('Delta Error Membership Functions')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
          # 3. Motor power membership functions
        power_levels = ['low', 'medium', 'high', 'very_high']
        power_colors = ['blue', 'green', 'orange', 'red']
        
        for i, level in enumerate(power_levels):
            membership_values = self.controller.motor_power[level].mf
            ax3.plot(self.controller.motor_power.universe, membership_values, 
                    label=level.replace('_', ' ').title(), color=power_colors[i], linewidth=2)
        ax3.set_xlabel('Motor Power (%)')
        ax3.set_ylabel('Membership')
        ax3.set_title('Motor Power Membership Functions')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Control surface (simplified 2D view)
        error_vals = np.linspace(0, 36, 50)
        delta_vals = np.linspace(-10, 10, 50)
        power_surface = np.zeros((len(delta_vals), len(error_vals)))
        
        for i, delta in enumerate(delta_vals):
            for j, error in enumerate(error_vals):
                try:
                    self.controller.simulation.input['error'] = error
                    self.controller.simulation.input['delta_error'] = delta
                    self.controller.simulation.compute()
                    power_surface[i, j] = self.controller.simulation.output['motor_power']
                except:
                    power_surface[i, j] = 0
        
        im = ax4.contourf(error_vals, delta_vals, power_surface, levels=20, cmap='viridis')
        ax4.set_xlabel('Error (m)')
        ax4.set_ylabel('Delta Error (m)')
        ax4.set_title('Fuzzy Control Surface')
        plt.colorbar(im, ax=ax4, label='Motor Power (%)')
        
        plt.tight_layout()
        return fig
    
    def run_analysis(self, save_plots=True):
        """Run complete analysis with all plots"""
        print("🚀 Starting Elevator Fuzzy Controller Analysis...")
        print("="*60)
          # Simulate all scenarios
        all_data = []
        
        # Create analysis directories if they don't exist
        import os
        os.makedirs("analysis/elevator_performance", exist_ok=True)
        
        for scenario in self.scenarios:
            data = self.simulate_scenario(scenario['start'], scenario['end'])
            all_data.append(data)
            
            # Plot individual scenario
            if save_plots:
                fig = self.plot_single_scenario(data)
                filename = f"analysis/elevator_performance/elevator_analysis_{scenario['start']}_to_{scenario['end']}.png"
                fig.savefig(filename, dpi=300, bbox_inches='tight')
                print(f"💾 Saved: {filename}")
                plt.close(fig)
        
        # Plot comparison
        print("\n📊 Creating comparison plots...")
        comparison_fig = self.plot_comparison(all_data)
        if save_plots:
            comparison_fig.savefig("analysis/elevator_performance/elevator_comparison_analysis.png", dpi=300, bbox_inches='tight')
            print("💾 Saved: analysis/elevator_performance/elevator_comparison_analysis.png")
        
        # Plot fuzzy analysis
        print("\n🧠 Creating fuzzy system analysis...")
        fuzzy_fig = self.plot_fuzzy_surfaces()
        if save_plots:
            fuzzy_fig.savefig("analysis/elevator_performance/elevator_fuzzy_analysis.png", dpi=300, bbox_inches='tight')
            print("💾 Saved: analysis/elevator_performance/elevator_fuzzy_analysis.png")
        
        # Show plots
        print("\n📈 Displaying plots...")
        comparison_fig.show()
        fuzzy_fig.show()
        
        # Summary statistics
        print("\n📋 PERFORMANCE SUMMARY:")
        print("="*60)
        for i, (scenario, data) in enumerate(zip(self.scenarios, all_data)):
            final_error = abs(data['error'][-1]) if data['error'] else 0
            max_power = max([abs(p) for p in data['motor_power']]) if data['motor_power'] else 0
            total_time = data['time'][-1] if data['time'] else 0
            
            print(f"{scenario['name']:12} | "
                  f"Time: {total_time:5.1f}s | "
                  f"Final Error: {final_error*1000:5.1f}mm | "
                  f"Max Power: {max_power:5.1f}%")
        
        print("="*60)
        print("🎉 Analysis complete! Check the generated plots.")
        
        # Keep plots open
        input("\nPress Enter to close plots and exit...")
        plt.close('all')

def main():
    """Main function"""
    print("🔬 Elevator Fuzzy Controller - Performance Analysis")
    print("This script will analyze motor power, delta error, and error graphics")
    print()
    
    plotter = ElevatorPlotter()
    plotter.run_analysis(save_plots=True)

if __name__ == "__main__":
    main()
