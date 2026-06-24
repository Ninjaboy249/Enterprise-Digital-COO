"""
WebSocket Manager for real-time updates
"""
from typing import Dict, List
from fastapi import WebSocket
import logging
import json

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections for real-time updates
    """
    
    def __init__(self):
        # Store active connections: client_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {str(e)}")
                self.disconnect(client_id)
    
    async def send_json(self, data: dict, client_id: str):
        """Send JSON data to a specific client"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error sending JSON to {client_id}: {str(e)}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected clients"""
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {str(e)}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def broadcast_json(self, data: dict):
        """Broadcast JSON data to all connected clients"""
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error broadcasting JSON to {client_id}: {str(e)}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def send_agent_update(self, agent_name: str, update: dict):
        """Send an agent update to all connected clients"""
        message = {
            "type": "agent_update",
            "agent": agent_name,
            "data": update,
            "timestamp": update.get("timestamp")
        }
        await self.broadcast_json(message)
    
    async def send_anomaly_alert(self, anomaly: dict):
        """Send an anomaly alert to all connected clients"""
        message = {
            "type": "anomaly_alert",
            "severity": anomaly.get("severity", "medium"),
            "data": anomaly,
            "timestamp": anomaly.get("timestamp")
        }
        await self.broadcast_json(message)
    
    async def send_recommendation(self, recommendation: dict):
        """Send a recommendation to all connected clients"""
        message = {
            "type": "recommendation",
            "priority": recommendation.get("priority", "medium"),
            "data": recommendation,
            "timestamp": recommendation.get("timestamp")
        }
        await self.broadcast_json(message)
    
    async def send_simulation_result(self, simulation: dict):
        """Send a simulation result to all connected clients"""
        message = {
            "type": "simulation_result",
            "scenario": simulation.get("scenario"),
            "data": simulation,
            "timestamp": simulation.get("timestamp")
        }
        await self.broadcast_json(message)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
    
    def get_connected_clients(self) -> List[str]:
        """Get list of connected client IDs"""
        return list(self.active_connections.keys())


# Create singleton instance
websocket_manager = WebSocketManager()

# Made with Bob