"""
Fuzzy Rules Visualization Script - Clean Version
"""

import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from elevator_fuzzy_controller import ElevatorFuzzyController

class FuzzyRulesPlotter:
    def __init__(self):
        self.controller = ElevatorFuzzyController()
        
        # Define rule mapping for visualization
        self.error_levels = ['very_small', 'small', 'medium', 'large']
        self.delta_levels = ['negative_large', 'negative_small', 'zero', 'positive_small', 'positive_large']
        self.power_levels = ['low', 'medium', 'high', 'very_high']
        
        # Create rule matrix
        self.rule_matrix = self._create_rule_matrix()
    
    def _create_rule_matrix(self):
        """Create a matrix representation of the fuzzy rules"""
        power_map = {'low': 1, 'medium': 2, 'high': 3, 'very_high': 4}
        matrix = np.zeros((len(self.delta_levels), len(self.error_levels)))
        
        # Updated rules matching the current elevator_fuzzy_controller.py
        rules = [
            # Very small error (0-0.8m) - chegando ao destino (regra simples sem delta_error)
            # Esta regra será representada com 'low' para todos os delta_error para visualização
            ('very_small', 'negative_large', 'low'),
            ('very_small', 'negative_small', 'low'),
            ('very_small', 'zero', 'low'),
            ('very_small', 'positive_small', 'low'),
            ('very_small', 'positive_large', 'low'),
            
            # Small error (~9m) - alvejando ~31.5%
            ('small', 'positive_large', 'medium'),
            ('small', 'positive_small', 'low'),
            ('small', 'zero', 'low'),
            ('small', 'negative_small', 'low'),
            ('small', 'negative_large', 'low'),
            
            # Medium error (~15m) - alvejando ~45%
            ('medium', 'positive_large', 'high'),
            ('medium', 'positive_small', 'medium'),
            ('medium', 'zero', 'medium'),
            ('medium', 'negative_small', 'medium'),
            ('medium', 'negative_large', 'low'),
            
            # Large error (~21m) - alvejando ~85-90%
            ('large', 'positive_large', 'very_high'),
            ('large', 'positive_small', 'very_high'),
            ('large', 'zero', 'very_high'),
            ('large', 'negative_small', 'high'),
            ('large', 'negative_large', 'medium'),
        ]
        
        for error, delta, power in rules:
            if error in self.error_levels and delta in self.delta_levels:
                error_idx = self.error_levels.index(error)
                delta_idx = self.delta_levels.index(delta)
                matrix[delta_idx, error_idx] = power_map[power]
        
        return matrix
    
    def plot_membership_functions(self):
        """Plot individual membership functions for each variable"""
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Fuzzy Membership Functions', fontsize=16, fontweight='bold')
        
        # Error membership functions
        colors = ['blue', 'green', 'orange', 'red']
        for i, level in enumerate(self.error_levels):
            membership_values = self.controller.error[level].mf
            ax1.plot(self.controller.error.universe, membership_values, 
                    label=level.replace('_', ' ').title(), color=colors[i], linewidth=2)
        
        ax1.set_xlabel('Error (m)', fontweight='bold')
        ax1.set_ylabel('Membership Value', fontweight='bold')
        ax1.set_title('Error Membership Functions', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 1.05)
        
        # Delta error membership functions
        delta_colors = ['red', 'orange', 'blue', 'green', 'purple']
        for i, level in enumerate(self.delta_levels):
            membership_values = self.controller.delta_error[level].mf
            ax2.plot(self.controller.delta_error.universe, membership_values, 
                    label=level.replace('_', ' ').title(), color=delta_colors[i], linewidth=2)
        
        ax2.set_xlabel('Delta Error (m/s)', fontweight='bold')
        ax2.set_ylabel('Membership Value', fontweight='bold')
        ax2.set_title('Delta Error Membership Functions', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 1.05)
        
        # Motor power membership functions
        power_colors = ['blue', 'green', 'orange', 'red']
        for i, level in enumerate(self.power_levels):
            membership_values = self.controller.motor_power[level].mf
            ax3.plot(self.controller.motor_power.universe, membership_values, 
                    label=level.replace('_', ' ').title(), color=power_colors[i], linewidth=2)
        
        ax3.set_xlabel('Motor Power (%)', fontweight='bold')
        ax3.set_ylabel('Membership Value', fontweight='bold')
        ax3.set_title('Motor Power Membership Functions', fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_ylim(0, 1.05)
        
        plt.tight_layout()
        return fig
    
    def plot_rule_table(self):
        """Plot the rule table as a heatmap"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        colors = ['white', '#E3F2FD', '#BBDEFB', '#90CAF9', '#1976D2']
        cmap = plt.cm.colors.ListedColormap(colors)
        
        im = ax.imshow(self.rule_matrix, cmap=cmap, aspect='auto', vmin=0, vmax=4)
        
        ax.set_xticks(range(len(self.error_levels)))
        ax.set_xticklabels([level.replace('_', ' ').title() for level in self.error_levels])
        ax.set_yticks(range(len(self.delta_levels)))
        ax.set_yticklabels([level.replace('_', ' ').title() for level in self.delta_levels])
        
        power_names = ['', 'Low (~31.5%)', 'Medium (~45%)', 'High (~70%)', 'Very High (~90%)']
        for i in range(len(self.delta_levels)):
            for j in range(len(self.error_levels)):
                value = int(self.rule_matrix[i, j])
                if value > 0:
                    text = power_names[value].split('(')[0].strip()  # Only show the name part
                    ax.text(j, i, text, ha="center", va="center", 
                           color="white" if value > 2 else "black", fontweight='bold')
        
        ax.set_xlabel('Error Level', fontsize=12, fontweight='bold')
        ax.set_ylabel('Delta Error Level', fontsize=12, fontweight='bold')
        ax.set_title('Fuzzy Rules Table\n(Error × Delta Error → Motor Power)', 
                    fontsize=14, fontweight='bold')
        
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_ticks(range(5))
        cbar.set_ticklabels(['None', 'Low (~31.5%)', 'Medium (~45%)', 'High (~70%)', 'Very High (~90%)'])
        cbar.set_label('Motor Power Level', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def plot_rule_surface(self):
        """Plot the fuzzy control surface"""
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        error_range = np.linspace(0, 36, 50)
        delta_range = np.linspace(-10, 10, 50)
        Error, Delta = np.meshgrid(error_range, delta_range)
        
        Power = np.zeros_like(Error)
        
        for i in range(Error.shape[0]):
            for j in range(Error.shape[1]):
                try:
                    self.controller.simulation.input['error'] = Error[i, j]
                    self.controller.simulation.input['delta_error'] = Delta[i, j]
                    self.controller.simulation.compute()
                    Power[i, j] = self.controller.simulation.output['motor_power']
                except:
                    Power[i, j] = 0
        
        surf = ax.plot_surface(Error, Delta, Power, cmap='viridis', 
                              alpha=0.8, linewidth=0, antialiased=True)
        
        ax.contour(Error, Delta, Power, zdir='z', offset=0, cmap='viridis', alpha=0.5)
        
        ax.set_xlabel('Error (m)', fontsize=10, fontweight='bold')
        ax.set_ylabel('Delta Error (m)', fontsize=10, fontweight='bold')
        ax.set_zlabel('Motor Power (%)', fontsize=10, fontweight='bold')
        ax.set_title('Fuzzy Control Surface\n(Based on Rules)', fontsize=12, fontweight='bold')
        
        plt.colorbar(surf, ax=ax, shrink=0.5, aspect=20, label='Motor Power (%)')
        
        return fig
    
    def plot_rule_activation(self, error_val, delta_val):
        """Plot rule activation for specific input values"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Rule Activation Analysis\nError = {error_val:.2f}m, Delta Error = {delta_val:.2f}m', 
                    fontsize=14, fontweight='bold')
        
        # Calculate membership values
        error_memberships = {}
        delta_memberships = {}
        
        for level in self.error_levels:
            error_memberships[level] = fuzz.interp_membership(
                self.controller.error.universe, 
                self.controller.error[level].mf, 
                error_val
            )
        
        for level in self.delta_levels:
            delta_memberships[level] = fuzz.interp_membership(
                self.controller.delta_error.universe, 
                self.controller.delta_error[level].mf, 
                delta_val
            )
        
        # Error membership plot
        bars1 = ax1.bar(range(len(self.error_levels)), 
                       [error_memberships[level] for level in self.error_levels],
                       color=['blue', 'green', 'orange', 'red'])
        ax1.set_xticks(range(len(self.error_levels)))
        ax1.set_xticklabels([level.replace('_', ' ').title() for level in self.error_levels], rotation=45)
        ax1.set_ylabel('Membership Value')
        ax1.set_title('Error Membership Activation')
        ax1.set_ylim(0, 1)
        ax1.grid(True, alpha=0.3)
        
        for bar, level in zip(bars1, self.error_levels):
            height = bar.get_height()
            if height > 0.01:
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                        f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # Delta error membership plot
        bars2 = ax2.bar(range(len(self.delta_levels)), 
                       [delta_memberships[level] for level in self.delta_levels],
                       color=['red', 'orange', 'blue', 'green', 'purple'])
        ax2.set_xticks(range(len(self.delta_levels)))
        ax2.set_xticklabels([level.replace('_', ' ').title() for level in self.delta_levels], rotation=45)
        ax2.set_ylabel('Membership Value')
        ax2.set_title('Delta Error Membership Activation')
        ax2.set_ylim(0, 1)
        ax2.grid(True, alpha=0.3)
        
        for bar, level in zip(bars2, self.delta_levels):
            height = bar.get_height()
            if height > 0.01:
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                        f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # Active rules
        active_rules = []
        rule_strengths = []
        
        for i, error_level in enumerate(self.error_levels):
            for j, delta_level in enumerate(self.delta_levels):
                error_membership = error_memberships[error_level]
                delta_membership = delta_memberships[delta_level]
                rule_strength = min(error_membership, delta_membership)
                
                if rule_strength > 0.01:
                    power_value = self.rule_matrix[j, i]
                    if power_value > 0:
                        power_name = self.power_levels[int(power_value)-1]
                        rule_text = f"IF {error_level.replace('_', ' ')} AND {delta_level.replace('_', ' ')} → {power_name.replace('_', ' ').title()}"
                        active_rules.append(rule_text)
                        rule_strengths.append(rule_strength)
        
        if active_rules:
            y_pos = range(len(active_rules))
            bars3 = ax3.barh(y_pos, rule_strengths, color='skyblue')
            ax3.set_yticks(y_pos)
            ax3.set_yticklabels([rule for rule in active_rules], fontsize=8)
            ax3.set_xlabel('Rule Strength')
            ax3.set_title('Active Rules')
            ax3.set_xlim(0, 1)
            ax3.grid(True, alpha=0.3)
        else:
            ax3.text(0.5, 0.5, 'No active rules', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Active Rules')
        
        # Final output
        try:
            self.controller.simulation.input['error'] = error_val
            self.controller.simulation.input['delta_error'] = delta_val
            self.controller.simulation.compute()
            final_output = self.controller.simulation.output['motor_power']
            
            ax4.bar(['Final Output'], [final_output], color='red', alpha=0.7)
            ax4.set_ylabel('Motor Power (%)')
            ax4.set_title('Defuzzified Output')
            ax4.set_ylim(0, 100)
            ax4.grid(True, alpha=0.3)
            ax4.text(0, final_output + 2, f'{final_output:.1f}%', ha='center', va='bottom', 
                    fontsize=12, fontweight='bold')
            
        except Exception as e:
            ax4.text(0.5, 0.5, f'Error: {str(e)}', ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Defuzzified Output')
        
        plt.tight_layout()
        return fig

if __name__ == "__main__":
    print("Fuzzy Rules Plotter - Available functions:")
    print("- plot_membership_functions()")
    print("- plot_rule_table()")
    print("- plot_rule_surface()")
    print("- plot_rule_activation(error, delta)")
