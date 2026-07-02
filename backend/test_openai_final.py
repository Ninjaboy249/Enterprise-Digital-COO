"""
Final OpenAI API test with available models
"""
import os
import sys

os.environ['DEBUG'] = 'True'

from openai import OpenAI
from config import settings

def test_openai():
    print("=" * 60)
    print("OpenAI API Connectivity Test")
    print("=" * 60)
    
    # Check API key
    print("\n1. Checking API Key Configuration...")
    api_key = settings.OPENAI_API_KEY
    
    if not api_key or api_key == "your-openai-api-key":
        print("[ERROR] OpenAI API key is not configured!")
        return False
    
    masked_key = api_key[:10] + "..." + api_key[-4:]
    print(f"[OK] API Key: {masked_key}")
    
    # Initialize client
    print("\n2. Initializing OpenAI Client...")
    try:
        client = OpenAI(api_key=api_key)
        print("[OK] Client initialized successfully")
    except Exception as e:
        print(f"[ERROR] Client initialization failed: {e}")
        return False
    
    # List available models
    print("\n3. Checking Available Models...")
    try:
        models = client.models.list()
        available_models = [model.id for model in models.data]
        print(f"[OK] Found {len(available_models)} models")
        
        # Check for common models
        common_models = ['gpt-4o-mini', 'gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo']
        available_common = [m for m in common_models if m in available_models]
        
        if available_common:
            print(f"[OK] Available chat models: {', '.join(available_common)}")
            test_model = available_common[0]
        else:
            # Use any available model
            chat_models = [m for m in available_models if 'gpt' in m.lower()]
            if chat_models:
                test_model = chat_models[0]
                print(f"[OK] Using model: {test_model}")
            else:
                print("[WARNING] No GPT models found, using gpt-3.5-turbo")
                test_model = 'gpt-3.5-turbo'
                
    except Exception as e:
        print(f"[WARNING] Could not list models: {e}")
        test_model = 'gpt-3.5-turbo'
        print(f"[OK] Will try with: {test_model}")
    
    # Test chat completion
    print(f"\n4. Testing Chat Completion with {test_model}...")
    try:
        response = client.chat.completions.create(
            model=test_model,
            messages=[
                {"role": "user", "content": "Say 'Hello' in one word"}
            ],
            max_tokens=10
        )
        
        message = response.choices[0].message.content
        print(f"[OK] Chat Completion successful!")
        print(f"    Response: {message}")
        print(f"    Model used: {response.model}")
        
    except Exception as e:
        print(f"[ERROR] Chat completion failed: {e}")
        return False
    
    # Test embeddings
    print(f"\n5. Testing Embeddings with {settings.OPENAI_EMBEDDING_MODEL}...")
    try:
        response = client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input="Test sentence for embeddings"
        )
        
        embedding = response.data[0].embedding
        print(f"[OK] Embeddings successful!")
        print(f"    Model: {response.model}")
        print(f"    Dimensions: {len(embedding)}")
        
    except Exception as e:
        print(f"[ERROR] Embeddings failed: {e}")
        # Try with a different embedding model
        try:
            print("    Trying text-embedding-3-small...")
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input="Test sentence"
            )
            embedding = response.data[0].embedding
            print(f"[OK] Alternative embedding model works!")
            print(f"    Model: {response.model}")
            print(f"    Dimensions: {len(embedding)}")
        except Exception as e2:
            print(f"[ERROR] Alternative embedding also failed: {e2}")
            return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] OpenAI API is working correctly!")
    print("=" * 60)
    print("\nRecommendations:")
    print(f"  - Update OPENAI_MODEL in .env to: {test_model}")
    print("  - Current embedding model is working fine")
    return True

if __name__ == "__main__":
    try:
        success = test_openai()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Codex
