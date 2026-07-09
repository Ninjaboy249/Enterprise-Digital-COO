"""
Test script to verify routes are properly configured
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_routes():
    """Test all routes"""
    print("Testing routes...")
    
    # Test health endpoint
    response = client.get("/health")
    print(f"OK /health: {response.status_code} - {response.json()}")
    
    # Test API v1 health
    response = client.get("/api/v1/health")
    print(f"OK /api/v1/health: {response.status_code} - {response.json()}")
    
    # Test metrics endpoints
    endpoints = [
        "/api/v1/metrics/sales",
        "/api/v1/metrics/finance",
        "/api/v1/metrics/operations",
        "/api/v1/metrics/summary",
        "/api/v1/notifications/integrations/status",
        "/api/v1/notifications/slack/status",
        "/api/v1/notifications/teams/status",
        "/api/v1/notifications/email/status",
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        if response.status_code == 200:
            print(f"OK {endpoint}: {response.status_code} - OK")
        else:
            print(f"FAIL {endpoint}: {response.status_code} - {response.json()}")
    
    # List all routes
    print("\nAll registered routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  {route.methods if hasattr(route, 'methods') else 'N/A'} {route.path}")

if __name__ == "__main__":
    test_routes()

# Made with Codex
