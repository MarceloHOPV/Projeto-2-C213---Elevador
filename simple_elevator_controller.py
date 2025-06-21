"""
Simplified elevator controller for testing without MQTT broker
This version simulates MQTT functionality for demonstration purposes
"""

import time
import threading
import asyncio
import logging
from typing import Optional, Callable
from elevator_fuzzy_controller import ElevatorFuzzyController
import json

logger = logging.getLogger(__name__)

class SimpleElevatorController:
    """
    Simplified elevator controller that works without external MQTT broker
    Simulates MQTT functionality for testing and demonstration
    """
    
    def __init__(self):
        self.controller = ElevatorFuzzyController()
        
        # Current elevator state
        self.current_floor = "terreo"
        self.current_position = 4.0  # Starting at ground floor
        self.target_floor = None
        self.target_position = None
        self.is_moving = False
        self.direction = 0  # 1 for up, -1 for down, 0 for stopped
        self.previous_error = 0.0
        
        # Movement simulation state
        self.simulation_thread = None
        self.stop_simulation = False
        
        # Callbacks
        self.position_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
          # Store event loop for thread-safe WebSocket broadcasts
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = None
        
        print("Simple Elevator Controller initialized (MQTT simulation mode)")
    
    def _safe_callback(self, callback, data):
        """Call callback in a thread-safe manner"""
        if callback:
            try:
                callback(data)
            except Exception as e:
                logger.debug(f"Callback error: {e}")
    
    def connect(self):
        """Simulate MQTT connection"""
        print("Simulated MQTT connection established")
        return True
    
    def disconnect(self):
        """Simulate MQTT disconnection"""
        self.stop_simulation = True
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join()
        print("Simulated MQTT connection closed")
    
    def move_to_floor(self, target_floor: str):
        """Initiate movement to target floor"""
        if self.is_moving:
            print("Elevator is already moving")
            return False
        
        try:
            # Validate floor
            target_position = self.controller.get_floor_position(target_floor)
            
            if abs(target_position - self.current_position) < 0.1:
                print(f"Already at floor {target_floor}")
                return False
            
            self.target_floor = target_floor
            self.target_position = target_position
            self.direction = 1 if target_position > self.current_position else -1
            self.is_moving = True
            self.previous_error = target_position - self.current_position
              # Start simulation in a separate thread
            self.stop_simulation = False
            self.simulation_thread = threading.Thread(target=self._run_movement_simulation)
            self.simulation_thread.start()
            
            # Publish status update
            self._publish_status_update()
            
            return True
            
        except ValueError as e:
            print(f"Invalid floor request: {e}")
            return False
    
    def _run_movement_simulation(self):
        """Run the real-time movement simulation with Linear Acceleration System"""
        tolerance = 0.02  # 2cm tolerance for precise stopping
        max_iterations = 300  # Maximum 60 seconds at 200ms sampling
        iteration = 0
          # Linear Acceleration System tracking
        movement_start_time = time.time()
        startup_direction = self.direction  # Store initial direction for startup phase
        
        # Variables to track movement stability
        position_history = []
        stable_count = 0
        required_stable_iterations = 5  # Need 5 stable readings to stop (1 second)
        min_movement_threshold = 0.001  # Minimum movement to consider progress (1mm)
        
        print(f"Starting movement from {self.current_floor} to {self.target_floor}")
        print(f"Linear Acceleration System: 0% → 31.5% over 2 seconds")
        
        while (not self.stop_simulation and 
               iteration < max_iterations):
            
            try:
                current_error = self.target_position - self.current_position
                
                # Check if we've reached the target with required precision
                if abs(current_error) <= tolerance:
                    stable_count += 1
                    print(f"At target (count {stable_count}/{required_stable_iterations}), error: {abs(current_error)*1000:.1f}mm")
                    if stable_count >= required_stable_iterations:
                        print(f"Target reached with stable position. Final error: {abs(current_error)*1000:.1f}mm")
                        break
                else:
                    stable_count = 0                # Check if we're in the Linear Acceleration System phase (first 2 seconds)
                elapsed_time = time.time() - movement_start_time
                startup_power = self.controller.compute_startup_power(elapsed_time, startup_direction)
                
                if startup_power is not None:
                    # Linear Acceleration System active (0-2 seconds)
                    motor_power = startup_power  # startup_power already has the correct sign
                    print(f"Startup phase: {elapsed_time:.1f}s, power: {abs(motor_power):.1f}%, direction: {startup_direction}")
                else:
                    # Normal fuzzy control (after 2 seconds) - now returns power with sign
                    motor_power, fuzzy_error = self.controller.compute_control(
                        self.current_position, 
                        self.target_position, 
                        self.previous_error
                    )
                    
                    # Update direction based on power sign (allows correction if overshot)
                    old_direction = self.direction
                    self.direction = 1 if motor_power > 0 else -1
                    
                    # Detect direction change (overshoot)
                    if old_direction != 0 and old_direction != self.direction:
                        print(f"Direction change detected (overshoot), power: {abs(motor_power):.1f}%, new direction: {self.direction}")
                
                # Force stop if error is very small
                if abs(current_error) <= tolerance:
                    motor_power = 0
                    print(f"Forcing stop - within tolerance")
                  # Apply minimum motor power threshold to avoid very slow movements
                elif abs(motor_power) < 3.0:  # Below 3% motor power
                    if abs(current_error) > tolerance * 2:  # Only if significantly far from target
                        motor_power = 3.0 * (1 if current_error > 0 else -1)
                        print(f"Applying minimum motor power: {motor_power}%")
                    else:
                        motor_power = 0  # Stop if close to target and low power
                        print(f"Low power and close to target - stopping")
                
                # Update position - motor_power now has the correct sign
                old_position = self.current_position
                # For startup phase, use startup direction; otherwise, extract direction from power sign
                if startup_power is not None:
                    current_direction = startup_direction
                else:
                    current_direction = 1 if motor_power > 0 else -1
                
                self.current_position = self.controller.update_position(
                    self.current_position, 
                    motor_power,  # Already has correct sign
                    current_direction  # But still pass direction for k1 calculation
                )
                
                # Track actual movement
                actual_movement = abs(self.current_position - old_position)
                
                # Track position history for oscillation detection
                position_history.append(self.current_position)
                if len(position_history) > 10:  # Keep last 10 positions
                    position_history.pop(0)
                
                # Check for oscillation (position bouncing around target)
                if len(position_history) >= 6:
                    recent_positions = position_history[-6:]
                    position_variance = max(recent_positions) - min(recent_positions)
                    if position_variance < tolerance * 2 and abs(current_error) < tolerance * 1.5:
                        print(f"Oscillation detected, stopping. Variance: {position_variance*1000:.1f}mm")
                        break
                
                # Check for stalled movement
                if len(position_history) >= 8:
                    recent_movement = abs(position_history[-1] - position_history[-8])
                    if recent_movement < min_movement_threshold and abs(current_error) > tolerance:
                        print(f"Movement stalled, recent movement: {recent_movement*1000:.1f}mm, error: {abs(current_error)*1000:.1f}mm")
                        if abs(current_error) <= tolerance * 3:  # Close enough to target
                            print("Close to target, stopping")
                            break
                        else:
                            # Force a correction movement
                            correction = tolerance/3 * (1 if current_error > 0 else -1)
                            self.current_position += correction
                            print(f"Applied correction: {correction*1000:.1f}mm")
                
                # Update previous error
                self.previous_error = current_error
                  # Create position update message
                position_data = {
                    'timestamp': time.time(),
                    'current_position': self.current_position,
                    'target_position': self.target_position,
                    'current_floor': self._get_nearest_floor(),
                    'target_floor': self.target_floor,
                    'motor_power': motor_power,  # Now includes proper sign
                    'error': current_error,
                    'direction': 'up' if motor_power > 0 else ('down' if motor_power < 0 else 'stopped'),
                    'is_moving': True
                }
                
                # Call position callback if set
                self._safe_callback(self.position_callback, position_data)
                  # Print progress - show power as positive, direction separately
                if iteration % 10 == 0:  # Print every 2 seconds
                    direction_str = "up" if motor_power > 0 else ("down" if motor_power < 0 else "stopped")
                    print(f"Position: {self.current_position:.2f}m, Motor: {abs(motor_power):.1f}%, Error: {current_error*1000:+.1f}mm, Dir: {direction_str}")
                
                iteration += 1
                time.sleep(self.controller.sampling_time)
                
            except Exception as e:
                print(f"Error in movement simulation: {e}")
                break
        
        # Movement completed or stopped
        self.is_moving = False
        self.direction = 0
        self.current_floor = self._get_nearest_floor()
        
        final_data = {
            'timestamp': time.time(),
            'current_position': self.current_position,
            'target_position': self.target_position,
            'current_floor': self.current_floor,
            'target_floor': self.target_floor,
            'motor_power': 0,
            'error': self.target_position - self.current_position,            'direction': 'stopped',
            'is_moving': False,
            'movement_completed': True
        }
        
        self._safe_callback(self.position_callback, final_data)
        
        self._publish_status_update()
        
        print(f"Movement completed. Current floor: {self.current_floor}")
        print(f"Final position: {self.current_position:.2f}m")
        print(f"Final error: {abs(self.target_position - self.current_position)*1000:.1f}mm")
    
    def _get_nearest_floor(self) -> str:
        """Get the nearest floor name based on current position"""
        min_distance = float('inf')
        nearest_floor = 'terreo'
        
        for floor_name, position in self.controller.floor_positions.items():
            distance = abs(position - self.current_position)
            if distance < min_distance:
                min_distance = distance
                nearest_floor = floor_name
        
        return nearest_floor
    
    def _publish_status_update(self):
        """Simulate publishing status update"""
        status_data = {
            'timestamp': time.time(),
            'current_floor': self.current_floor,
            'target_floor': self.target_floor,
            'is_moving': self.is_moving,
            'direction': 'up' if self.direction > 0 else ('down' if self.direction < 0 else 'stopped'),
            'current_position': self.current_position
        }
        
        print(f"DEBUG: Publishing status update - is_moving: {self.is_moving}, floor: {self.current_floor}")
        self._safe_callback(self.status_callback, status_data)
    
    def emergency_stop(self):
        """Emergency stop the elevator"""
        self.stop_simulation = True
        self.is_moving = False
        self.direction = 0
        self.target_floor = None
        self.target_position = None
        
        emergency_data = {
            'timestamp': time.time(),
            'current_position': self.current_position,
            'current_floor': self._get_nearest_floor(),
            'emergency_stopped': True,
            'is_moving': False        }
        
        self._safe_callback(self.position_callback, emergency_data)
        
        self._publish_status_update()
        
        print("Emergency stop executed!")
    
    def get_current_status(self) -> dict:
        """Get current elevator status"""
        return {
            'current_floor': self.current_floor,
            'current_position': self.current_position,
            'target_floor': self.target_floor,
            'target_position': self.target_position,
            'is_moving': self.is_moving,
            'direction': 'up' if self.direction > 0 else ('down' if self.direction < 0 else 'stopped')
        }
    
    def set_position_callback(self, callback: Callable):
        """Set callback for position updates"""
        self.position_callback = callback
    
    def set_status_callback(self, callback: Callable):
        """Set callback for status updates"""
        self.status_callback = callback

# Test function
def test_simple_controller():
    """Test the simple controller functionality"""
    
    def position_update_handler(data):
        print(f"Position: {data['current_position']:.2f}m, Motor: {data['motor_power']:.1f}%, Error: {data['error']:.3f}m")
    
    def status_update_handler(data):
        print(f"Status: Floor {data['current_floor']}, Moving: {data['is_moving']}, Direction: {data['direction']}")
    
    # Create controller
    controller = SimpleElevatorController()
    controller.set_position_callback(position_update_handler)
    controller.set_status_callback(status_update_handler)
    
    controller.connect()
    
    try:
        # Test movement
        time.sleep(2)
        print("\n--- Testing movement to Andar 3 ---")
        controller.move_to_floor('andar_3')
        
        # Wait for movement to complete
        while controller.is_moving:
            time.sleep(1)
        
        time.sleep(2)
        print("\n--- Testing movement back to Terreo ---")
        controller.move_to_floor('terreo')
        
        # Wait for movement to complete
        while controller.is_moving:
            time.sleep(1)
        
        print("\nTest completed successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        controller.disconnect()
        print("Controller disconnected")

if __name__ == "__main__":
    test_simple_controller()
