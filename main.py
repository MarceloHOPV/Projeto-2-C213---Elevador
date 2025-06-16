from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import asyncio
import time
from typing import List, Dict
import uvicorn
from elevator_fuzzy_controller import ElevatorFuzzyController
import threading
import logging

# Try to import MQTT client, fall back to simple controller if not available
try:
    from elevator_mqtt_client import ElevatorMQTTClient
    MQTT_AVAILABLE = True
except ImportError:
    from simple_elevator_controller import SimpleElevatorController as ElevatorMQTTClient
    MQTT_AVAILABLE = False
    print("Warning: MQTT client not available, using simple controller for demonstration")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Elevator Fuzzy Control System", description="Real-time elevator control with fuzzy logic")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global variables
mqtt_client = None
controller = ElevatorFuzzyController()
movement_data = []
current_status = {
    'current_floor': 'terreo',
    'current_position': 4.0,
    'target_floor': None,
    'is_moving': False,
    'direction': 'stopped'
}

# Message queue for thread-safe communication
message_queue = asyncio.Queue()

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, message: str):
        print(f"DEBUG: Broadcasting to {len(self.active_connections)} connections")
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
                print(f"DEBUG: Message sent to WebSocket connection")
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

def position_update_handler(data):
    """Handle position updates from MQTT client - thread-safe"""
    global movement_data, current_status
    
    print(f"DEBUG: Position update received - pos: {data.get('current_position'):.2f}m, motor: {data.get('motor_power'):.1f}%")
    
    # Update current status
    current_status.update({
        'current_floor': data.get('current_floor', current_status['current_floor']),
        'current_position': data.get('current_position', current_status['current_position']),
        'target_floor': data.get('target_floor', current_status['target_floor']),
        'is_moving': data.get('is_moving', current_status['is_moving']),
        'direction': data.get('direction', current_status['direction'])
    })
    
    # Add to movement data with timestamp
    movement_data.append({
        'timestamp': data.get('timestamp', time.time()),
        'position': data.get('current_position', 0),
        'target_position': data.get('target_position', 0),
        'motor_power': data.get('motor_power', 0),
        'error': data.get('error', 0)
    })
    # Keep only last 1000 data points
    if len(movement_data) > 1000:
        movement_data = movement_data[-1000:]
    
    # Put message in queue for async processing
    try:
        message_queue.put_nowait({
            'type': 'position_update',
            'data': data
        })
        print(f"DEBUG: Position update queued for broadcast")
    except asyncio.QueueFull:
        print(f"DEBUG: Message queue full, dropping position update")

def status_update_handler(data):
    """Handle status updates from MQTT client - thread-safe"""
    global current_status
    
    print(f"DEBUG: Status update received - is_moving: {data.get('is_moving')}, floor: {data.get('current_floor')}")
    
    current_status.update(data)
    
    # Put message in queue for async processing
    try:
        message_queue.put_nowait({
            'type': 'status_update',
            'data': data
        })
        print(f"DEBUG: Status update queued for broadcast")
    except asyncio.QueueFull:
        print(f"DEBUG: Message queue full, dropping status update")

async def message_broadcaster():
    """Background task to process message queue and broadcast to WebSockets"""
    while True:
        try:
            # Wait for messages in the queue
            message = await message_queue.get()
            
            # Broadcast the message
            await manager.broadcast(json.dumps(message))
            print(f"DEBUG: Message broadcasted: {message['type']}")
            
            # Mark task as done
            message_queue.task_done()
            
        except Exception as e:
            print(f"DEBUG: Error in message broadcaster: {e}")
            await asyncio.sleep(0.1)

def initialize_mqtt():
    """Initialize MQTT client with handlers"""
    global mqtt_client
    
    if MQTT_AVAILABLE:
        mqtt_client = ElevatorMQTTClient()
    else:
        mqtt_client = ElevatorMQTTClient()
    
    # Set handlers
    mqtt_client.position_callback = position_update_handler
    mqtt_client.status_callback = status_update_handler
    
    # Connect
    if mqtt_client.connect():
        print("MQTT client connected successfully")
        return True
    else:
        print("Failed to connect MQTT client")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    # Start message broadcaster
    asyncio.create_task(message_broadcaster())
    
    # Initialize MQTT in a separate thread
    def init_mqtt():
        initialize_mqtt()
    
    mqtt_thread = threading.Thread(target=init_mqtt, daemon=True)
    mqtt_thread.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if mqtt_client:
        mqtt_client.disconnect()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main dashboard page"""
    floor_positions = controller.floor_positions
    available_floors = ['terreo'] + [f'andar_{i}' for i in range(1, 9)]
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "available_floors": available_floors,
        "floor_positions": floor_positions,
        "current_status": current_status
    })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    
    try:
        # Send initial status
        await manager.send_personal_message(json.dumps({
            'type': 'initial_status',
            'data': current_status
        }), websocket)
        
        # Send recent movement data
        await manager.send_personal_message(json.dumps({
            'type': 'movement_data',
            'data': movement_data[-100:] if movement_data else []
        }), websocket)
        
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_websocket_message(message, websocket)
            except json.JSONDecodeError:
                await manager.send_personal_message(json.dumps({
                    'type': 'error',
                    'message': 'Invalid JSON format'
                }), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def handle_websocket_message(message: dict, websocket: WebSocket):
    """Handle incoming WebSocket messages"""
    message_type = message.get('type')
    
    if message_type == 'floor_request':
        floor = message.get('floor')
        if floor and mqtt_client:
            success = mqtt_client.move_to_floor(floor)
            await manager.send_personal_message(json.dumps({
                'type': 'floor_request_response',
                'success': success,
                'floor': floor,
                'message': f'{"Movement started" if success else "Movement failed"} to floor {floor}'
            }), websocket)
        else:
            await manager.send_personal_message(json.dumps({
                'type': 'floor_request_response',
                'success': False,
                'message': 'Invalid floor or MQTT client not available'
            }), websocket)
    
    elif message_type == 'emergency_stop':
        if mqtt_client and hasattr(mqtt_client, 'emergency_stop'):
            mqtt_client.emergency_stop()
        await manager.send_personal_message(json.dumps({
            'type': 'emergency_stop_response',
            'message': 'Emergency stop activated'
        }), websocket)
    
    elif message_type == 'get_status':
        await manager.send_personal_message(json.dumps({
            'type': 'status_update',
            'data': current_status
        }), websocket)

@app.get("/api/status")
async def get_status():
    """Get current elevator status"""
    return current_status

@app.get("/api/movement-data")
async def get_movement_data(limit: int = 100):
    """Get recent movement data"""
    return movement_data[-limit:] if movement_data else []

@app.post("/api/move-to-floor")
async def move_to_floor(request: Request):
    """Move elevator to specified floor"""
    data = await request.json()
    floor = data.get('floor')
    
    if not floor or not mqtt_client:
        return {"success": False, "message": "Invalid request or MQTT client not available"}
    
    success = mqtt_client.move_to_floor(floor)
    return {
        "success": success,
        "message": f"Movement {'started' if success else 'failed'} to floor {floor}",
        "current_status": current_status
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
