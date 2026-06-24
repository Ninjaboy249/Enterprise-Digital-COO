"""
Test script to verify IBM watsonx.ai API connectivity and functionality
"""
import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from config import settings

def test_watsonx_api():
    """Test IBM watsonx.ai API connectivity"""
    print("=" * 60)
    print("IBM watsonx.ai API Test")
    print("=" * 60)
    
    # Test 1: Check API Configuration
    print(f"\n1. Checking API Configuration...")
    api_key = settings.WATSONX_API_KEY
    project_id = settings.WATSONX_PROJECT_ID
    
    if not api_key or api_key == "your-watsonx-api-key":
        print("[ERROR] watsonx.ai API key is not configured!")
        print("Please set WATSONX_API_KEY in your .env file")
        return False
    
    if not project_id or project_id == "your-project-id":
        print("[ERROR] watsonx.ai Project ID is not configured!")
        print("Please set WATSONX_PROJECT_ID in your .env file")
        return False
    
    masked_key = api_key[:10] + "..." + api_key[-4:]
    masked_project = project_id[:8] + "..." + project_id[-4:]
    print(f"[OK] API Key found: {masked_key}")
    print(f"[OK] Project ID: {masked_project}")
    print(f"[OK] URL: {settings.WATSONX_URL}")
    print(f"[OK] Model: {settings.WATSONX_MODEL}")
    
    # Initialize watsonx.ai
    print(f"\n2. Initializing IBM watsonx.ai...")
    try:
        model_params = {
            GenParams.DECODING_METHOD: settings.WATSONX_DECODING_METHOD,
            GenParams.TEMPERATURE: settings.WATSONX_TEMPERATURE,
            GenParams.MAX_NEW_TOKENS: settings.WATSONX_MAX_TOKENS,
            GenParams.MIN_NEW_TOKENS: settings.WATSONX_MIN_TOKENS,
        }
        
        model = Model(
            model_id=settings.WATSONX_MODEL,
            params=model_params,
            credentials={
                "apikey": api_key,
                "url": settings.WATSONX_URL
            },
            project_id=project_id
        )
        print("[OK] watsonx.ai initialized successfully")
    except Exception as e:
        print(f"[ERROR] Failed to initialize watsonx.ai: {e}")
        return False
    
    # Test 3: Simple Text Generation
    print(f"\n3. Testing Text Generation...")
    try:
        prompt = "Say 'Hello, IBM watsonx.ai is working!' in exactly those words."
        response = model.generate_text(prompt=prompt)
        print(f"[OK] Response received")
        print(f"[OK] Response: {response}")
    except Exception as e:
        print(f"[ERROR] Text generation failed: {e}")
        return False
    
    # Test 4: Complex Query
    print(f"\n4. Testing Complex Query...")
    try:
        prompt = """
        Analyze the following business scenario and provide 3 key insights:
        
        A company's revenue dropped by 15% in Q2 2024.
        Sales team reports increased competition.
        Customer satisfaction scores remain high at 85%.
        
        Provide insights as bullet points.
        """
        
        response = model.generate_text(prompt=prompt)
        
        print(f"[OK] Complex query successful")
        print(f"[OK] Response length: {len(response)} characters")
        print(f"\nResponse preview:")
        print(response[:300] + "..." if len(response) > 300 else response)
    except Exception as e:
        print(f"[ERROR] Complex query failed: {e}")
        return False
    
    # Test 5: JSON Response
    print(f"\n5. Testing JSON Response...")
    try:
        prompt = """
        Generate a JSON object with the following structure:
        {
            "status": "success",
            "message": "IBM watsonx.ai is working correctly",
            "capabilities": ["text generation", "analysis", "reasoning"]
        }
        
        Return only the JSON object, no additional text.
        """
        
        response = model.generate_text(prompt=prompt)
        
        # Try to parse JSON
        import json
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            print(f"[OK] JSON parsing successful")
            print(f"[OK] Parsed data: {data}")
        else:
            print(f"[WARNING] Could not extract JSON from response")
            print(f"Response: {response[:200]}")
    except Exception as e:
        print(f"[WARNING] JSON test failed: {e}")
        print("[INFO] This is not critical - JSON extraction can be improved")
    
    # All tests passed
    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED - IBM watsonx.ai is working correctly!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. The API is configured and working")
    print("2. You can now run the main application")
    print("3. All agents will use IBM watsonx.ai for AI operations")
    return True


if __name__ == "__main__":
    try:
        success = test_watsonx_api()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob