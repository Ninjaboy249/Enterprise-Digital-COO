"""
Simple OpenAI API test script
"""
import os
import sys

# Set environment variable to avoid proxy issues
os.environ['DEBUG'] = 'True'

from openai import OpenAI
from config import settings

def test_openai():
    print("=" * 60)
    print("OpenAI API Simple Test")
    print("=" * 60)
    
    # Check API key
    print("\n1. Checking API Key...")
    api_key = settings.OPENAI_API_KEY
    
    if not api_key or api_key == "your-openai-api-key":
        print("[ERROR] OpenAI API key is not configured!")
        return False
    
    masked_key = api_key[:10] + "..." + api_key[-4:]
    print(f"[OK] API Key: {masked_key}")
    print(f"[OK] Model: {settings.OPENAI_MODEL}")
    
    # Initialize client
    print("\n2. Initializing OpenAI Client...")
    try:
        client = OpenAI(api_key=api_key)
        print("[OK] Client initialized")
    except Exception as e:
        print(f"[ERROR] Client initialization failed: {e}")
        return False
    
    # Test chat completion
    print("\n3. Testing Chat Completion...")
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "user", "content": "Say 'API is working' in 3 words"}
            ],
            max_tokens=20
        )
        
        message = response.choices[0].message.content
        print(f"[OK] Response: {message}")
        print(f"[OK] Model: {response.model}")
        
    except Exception as e:
        print(f"[ERROR] Chat completion failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False
    
    # Test embeddings
    print("\n4. Testing Embeddings...")
    try:
        response = client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input="Test sentence"
        )
        
        embedding = response.data[0].embedding
        print(f"[OK] Embedding dimensions: {len(embedding)}")
        
    except Exception as e:
        print(f"[ERROR] Embeddings failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] OpenAI API is working correctly!")
    print("=" * 60)
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

# Made with Bob
