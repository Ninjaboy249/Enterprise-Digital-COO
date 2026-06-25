"""
Verify that all necessary files exist and are properly configured
"""
import os
from pathlib import Path

def verify_setup():
    """Verify the setup"""
    print("Verifying Enterprise Digital COO setup...\n")
    
    # Check if files exist
    files_to_check = [
        "main.py",
        "config.py",
        ".env",
        "api/v1/router.py",
        "api/v1/endpoints/metrics.py",
        "api/v1/endpoints/__init__.py",
        "agents/base_agent.py",
        "agents/executive_decision_agent.py",
    ]
    
    print("Checking files:")
    all_exist = True
    for file_path in files_to_check:
        exists = Path(file_path).exists()
        status = "[OK]" if exists else "[MISSING]"
        print(f"  {status} {file_path}")
        if not exists:
            all_exist = False
    
    print()
    
    # Check .env configuration
    print("Checking .env configuration:")
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            
        required_vars = [
            "OPENAI_API_KEY",
            "OPENAI_MODEL",
            "DEBUG",
            "API_V1_PREFIX"
        ]
        
        for var in required_vars:
            if var in content:
                # Get the value
                for line in content.split('\n'):
                    if line.startswith(var):
                        value = line.split('=', 1)[1] if '=' in line else ''
                        # Mask API key
                        if 'KEY' in var and len(value) > 10:
                            value = value[:10] + '...' + value[-10:]
                        print(f"  [OK] {var}={value}")
                        break
            else:
                print(f"  [MISSING] {var} not found")
    else:
        print("  [MISSING] .env file not found")
    
    print()
    
    # Check metrics.py content
    print("Checking metrics.py endpoints:")
    metrics_file = Path("api/v1/endpoints/metrics.py")
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            content = f.read()
        
        endpoints = [
            "@router.get(\"/sales\")",
            "@router.get(\"/finance\")",
            "@router.get(\"/operations\")",
            "@router.get(\"/summary\")"
        ]
        
        for endpoint in endpoints:
            if endpoint in content:
                print(f"  [OK] {endpoint}")
            else:
                print(f"  [MISSING] {endpoint} not found")
    else:
        print("  [MISSING] metrics.py not found")
    
    print()
    
    # Check router.py
    print("Checking router.py configuration:")
    router_file = Path("api/v1/router.py")
    if router_file.exists():
        with open(router_file, 'r') as f:
            content = f.read()
        
        checks = [
            ("from api.v1.endpoints import metrics", "metrics import"),
            ("api_router.include_router(metrics.router", "metrics router included")
        ]
        
        for check_str, description in checks:
            if check_str in content:
                print(f"  [OK] {description}")
            else:
                print(f"  [MISSING] {description} not found")
    else:
        print("  [MISSING] router.py not found")
    
    print("\n" + "="*60)
    if all_exist:
        print("[SUCCESS] All files exist and configuration looks correct!")
        print("\nNEXT STEP: Restart the FastAPI server to load the new routes:")
        print("  1. Stop the current server (Ctrl+C)")
        print("  2. Run: python main.py")
        print("  3. Test at: http://localhost:8000/")
    else:
        print("[ERROR] Some files are missing. Please check the setup.")
    print("="*60)

if __name__ == "__main__":
    verify_setup()

# Made with Bob
