import paho.mqtt.client as mqtt
import json
import time
import threading
from typing import Optional, Callable
from elevator_fuzzy_controller import ElevatorFuzzyController

class ElevatorMQTTClient:
    """
    MQTT client for real-time elevator control communication
    """
    
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client()
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
        
        # MQTT topics
        self.topics = {
            'floor_request': 'elevator/floor_request',
            'position_update': 'elevator/position_update',
            'status_update': 'elevator/status_update',
            'emergency_stop': 'elevator/emergency_stop'
        }
        
        # Setup MQTT callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client receives a CONNACK response from the server"""
        if rc == 0:
            print(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            # Subscribe to relevant topics
            for topic in [self.topics['floor_request'], self.topics['emergency_stop']]:
                client.subscribe(topic)
                print(f"Subscribed to topic: {topic}")
        else:
            print(f"Failed to connect to MQTT broker. Return code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback for when a PUBLISH message is received from the server"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            if topic == self.topics['floor_request']:
                self._handle_floor_request(payload)
            elif topic == self.topics['emergency_stop']:
                self._handle_emergency_stop(payload)
                
        except json.JSONDecodeError:
            print(f"Invalid JSON received on topic {msg.topic}: {msg.payload}")
        except Exception as e:
            print(f"Error processing message on topic {msg.topic}: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker"""
        print(f"Disconnected from MQTT broker. Return code: {rc}")
    
    def _handle_floor_request(self, payload):
        """Handle floor request message"""
        try:
            requested_floor = payload.get('floor')
            if requested_floor and not self.is_moving:
                print(f"Floor request received: {requested_floor}")
                self.move_to_floor(requested_floor)
            elif self.is_moving:
                print(f"Elevator is moving. Request for {requested_floor} ignored.")
        except Exception as e:
            print(f"Error handling floor request: {e}")
    
    def _handle_emergency_stop(self, payload):
        """Handle emergency stop message"""
        print("Emergency stop activated!")
        self.emergency_stop()
    
    def connect(self):
        """Connect to the MQTT broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the MQTT broker"""
        self.stop_simulation = True
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join()
        self.client.loop_stop()
        self.client.disconnect()
    
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
        """Run the real-time movement simulation"""
        tolerance = 0.1  # 10cm tolerance
        max_iterations = 300  # Maximum 60 seconds at 200ms sampling
        iteration = 0
        
        print(f"Starting movement from {self.current_floor} to {self.target_floor}")
        
        while (not self.stop_simulation and 
               iteration < max_iterations and 
               abs(self.target_position - self.current_position) > tolerance):
            
            try:
                # Compute fuzzy control
                motor_power, current_error = self.controller.compute_control(
                    self.current_position, 
                    self.target_position, 
                    self.previous_error
                )
                
                # Update position
                self.current_position = self.controller.update_position(
                    self.current_position, 
                    motor_power, 
                    self.direction
                )
                
                # Update previous error
                self.previous_error = current_error
                
                # Create position update message
                position_data = {
                    'timestamp': time.time(),
                    'current_position': self.current_position,
                    'target_position': self.target_position,
                    'current_floor': self._get_nearest_floor(),
                    'target_floor': self.target_floor,
                    'motor_power': motor_power,
                    'error': current_error,
                    'direction': 'up' if self.direction > 0 else 'down',
                    'is_moving': True
                }
                
                # Publish position update
                self._publish_position_update(position_data)
                
                # Call position callback if set
                if self.position_callback:
                    self.position_callback(position_data)
                
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
            'error': self.target_position - self.current_position,
            'direction': 'stopped',
            'is_moving': False,
            'movement_completed': True
        }
        
        self._publish_position_update(final_data)
        self._publish_status_update()
        
        if self.position_callback:
            self.position_callback(final_data)
        
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
    
    def _publish_position_update(self, data: dict):
        """Publish position update to MQTT"""
        try:
            self.client.publish(self.topics['position_update'], json.dumps(data))
        except Exception as e:
            print(f"Error publishing position update: {e}")
    
    def _publish_status_update(self):
        """Publish status update to MQTT"""
        try:
            status_data = {
                'timestamp': time.time(),
                'current_floor': self.current_floor,
                'target_floor': self.target_floor,
                'is_moving': self.is_moving,
                'direction': 'up' if self.direction > 0 else ('down' if self.direction < 0 else 'stopped'),
                'current_position': self.current_position
            }
            
            self.client.publish(self.topics['status_update'], json.dumps(status_data))
            
            if self.status_callback:
                self.status_callback(status_data)
                
        except Exception as e:
            print(f"Error publishing status update: {e}")
    
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
            'is_moving': False
        }
        
        self._publish_position_update(emergency_data)
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
def test_mqtt_client():
    """Test the MQTT client functionality"""
    
    def position_update_handler(data):
        print(f"Position: {data['current_position']:.2f}m, Motor: {data['motor_power']:.1f}%, Error: {data['error']:.3f}m")
    
    def status_update_handler(data):
        print(f"Status: Floor {data['current_floor']}, Moving: {data['is_moving']}, Direction: {data['direction']}")
    
    # Create and connect MQTT client
    mqtt_client = ElevatorMQTTClient()
    mqtt_client.set_position_callback(position_update_handler)
    mqtt_client.set_status_callback(status_update_handler)
    
    if mqtt_client.connect():
        print("MQTT client connected successfully")
        
        try:
            # Test movement
            time.sleep(2)
            print("\n--- Testing movement to Andar 3 ---")
            mqtt_client.move_to_floor('andar_3')
            
            # Wait for movement to complete
            while mqtt_client.is_moving:
                time.sleep(1)
            
            time.sleep(2)
            print("\n--- Testing movement back to Terreo ---")
            mqtt_client.move_to_floor('terreo')
            
            # Wait for movement to complete
            while mqtt_client.is_moving:
                time.sleep(1)
            
            print("\nTest completed successfully!")
            
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
        finally:
            mqtt_client.disconnect()
            print("MQTT client disconnected")
    else:
        print("Failed to connect MQTT client")

if __name__ == "__main__":
    test_mqtt_client()
