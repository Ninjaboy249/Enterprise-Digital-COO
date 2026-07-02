"""
Test script to list available Gemini models
"""
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

try:
    import google.generativeai as genai
    from config import settings
    
    print("=" * 60)
    print("Gemini Available Models Test")
    print("=" * 60)
    
    # Configure Gemini
    api_key = settings.GEMINI_API_KEY
    print(f"\nAPI Key: {api_key[:10]}...{api_key[-4:]}")
    
    genai.configure(api_key=api_key)
    
    print("\nListing available models...")
    print("-" * 60)
    
    try:
        models = genai.list_models()
        count = 0
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                count += 1
                print(f"[OK] {model.name}")
                print(f"     Display Name: {model.display_name}")
                print(f"     Description: {model.description[:80]}...")
                print()
        
        if count == 0:
            print("[WARNING] No models found that support generateContent")
            print("This API key may not be valid for Google Gemini.")
        else:
            print(f"\n[SUCCESS] Found {count} available models")
            
    except Exception as e:
        print(f"[ERROR] Failed to list models: {e}")
        print("\nThis API key may not be valid for Google Gemini.")
        print("Please get a valid API key from: https://makersuite.google.com/app/apikey")
        sys.exit(1)
    
    print("=" * 60)
    
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

# Made with Codex
