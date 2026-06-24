"""
Test script to verify Gemini API connectivity and functionality
"""
import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

import google.generativeai as genai
from config import settings

def test_gemini_api():
    """Test Gemini API connectivity"""
    print("=" * 60)
    print("Gemini API Test")
    print("=" * 60)
    
    # Test 1: Check API Key Configuration
    print(f"\n1. Checking API Key Configuration...")
    api_key = settings.GEMINI_API_KEY
    
    if not api_key or api_key == "your-gemini-api-key":
        print("[ERROR] Gemini API key is not configured!")
        print("Please set GEMINI_API_KEY in your .env file")
        return False
    
    masked_key = api_key[:10] + "..." + api_key[-4:]
    print(f"[OK] API Key found: {masked_key}")
    print(f"[OK] Model: {settings.GEMINI_MODEL}")
    print(f"[OK] Embedding Model: {settings.GEMINI_EMBEDDING_MODEL}")
    
    # Initialize Gemini
    print(f"\n2. Initializing Gemini...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        print("[OK] Gemini initialized successfully")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Gemini: {e}")
        return False
    
    # Test 3: Simple Text Generation
    print(f"\n3. Testing Text Generation...")
    try:
        response = model.generate_content("Say 'Hello, Gemini API is working!' in exactly those words.")
        print(f"[OK] Response received")
        print(f"[OK] Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Text generation failed: {e}")
        return False
    
    # Test 4: Embeddings (if available)
    print(f"\n4. Testing Embeddings...")
    try:
        result = genai.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            content="This is a test sentence for embeddings.",
            task_type="retrieval_document"
        )
        embedding = result['embedding']
        print(f"[OK] Embedding generated")
        print(f"[OK] Embedding dimensions: {len(embedding)}")
    except Exception as e:
        print(f"[WARNING] Embedding test failed: {e}")
        print("[INFO] Embeddings may not be available in your Gemini plan")
    
    # Test 5: Complex Query
    print(f"\n5. Testing Complex Query...")
    try:
        prompt = """
        Analyze the following business scenario and provide 3 key insights:
        
        A company's revenue dropped by 15% in Q2 2024.
        Sales team reports increased competition.
        Customer satisfaction scores remain high at 85%.
        
        Provide insights as bullet points.
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=settings.GEMINI_TEMPERATURE,
                max_output_tokens=settings.GEMINI_MAX_TOKENS
            )
        )
        
        print(f"[OK] Complex query successful")
        print(f"[OK] Response length: {len(response.text)} characters")
        print(f"\nResponse preview:")
        print(response.text[:200] + "..." if len(response.text) > 200 else response.text)
    except Exception as e:
        print(f"[ERROR] Complex query failed: {e}")
        return False
    
    # All tests passed
    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED - Gemini API is working correctly!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = test_gemini_api()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        sys.exit(1)

# Made with Bob