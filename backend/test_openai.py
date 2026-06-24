"""
Test script to verify OpenAI API connectivity and functionality
"""
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from openai import OpenAI
from config import settings

def test_openai_api():
    """Test OpenAI API connectivity"""
    print("=" * 60)
    print("OpenAI API Test")
    print("=" * 60)
    
    # Check if API key is set
    print(f"\n1. Checking API Key Configuration...")
    api_key = settings.OPENAI_API_KEY
    
    if not api_key or api_key == "your-openai-api-key":
        print("[ERROR] OpenAI API key is not configured!")
        print("Please set OPENAI_API_KEY in your .env file")
        return False
    
    # Mask the API key for security
    masked_key = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
    print(f"[OK] API Key found: {masked_key}")
    print(f"[OK] Model: {settings.OPENAI_MODEL}")
    print(f"[OK] Embedding Model: {settings.OPENAI_EMBEDDING_MODEL}")
    
    # Initialize OpenAI client
    print(f"\n2. Initializing OpenAI Client...")
    try:
        client = OpenAI(api_key=api_key)
        print("[OK] OpenAI client initialized successfully")
    except Exception as e:
        print(f"[ERROR] Failed to initialize OpenAI client: {e}")
        return False
    
    # Test Chat Completion
    print(f"\n3. Testing Chat Completion API...")
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, OpenAI API is working!' in exactly those words."}
            ],
            max_tokens=50,
            temperature=0.0
        )
        
        message = response.choices[0].message.content
        print(f"[OK] Chat Completion successful!")
        print(f"  Response: {message}")
        print(f"  Model used: {response.model}")
        if response.usage:
            print(f"  Tokens used: {response.usage.total_tokens}")
        
    except Exception as e:
        print(f"[ERROR] Chat Completion failed: {e}")
        return False
    
    # Test Embeddings
    print(f"\n4. Testing Embeddings API...")
    try:
        response = client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input="This is a test sentence for embeddings."
        )
        
        embedding = response.data[0].embedding
        print(f"[OK] Embeddings successful!")
        print(f"  Model used: {response.model}")
        print(f"  Embedding dimensions: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
        
    except Exception as e:
        print(f"[ERROR] Embeddings failed: {e}")
        return False
    
    # Test with a business-related query
    print(f"\n5. Testing Business Query...")
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert business analyst."},
                {"role": "user", "content": "What are the top 3 reasons for revenue decline in a SaaS company? Be brief."}
            ],
            max_tokens=200,
            temperature=settings.OPENAI_TEMPERATURE
        )
        
        message = response.choices[0].message.content
        print(f"[OK] Business query successful!")
        print(f"  Response:\n{message}")
        
    except Exception as e:
        print(f"[ERROR] Business query failed: {e}")
        return False
    
    # All tests passed
    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED - OpenAI API is working correctly!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = test_openai_api()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
