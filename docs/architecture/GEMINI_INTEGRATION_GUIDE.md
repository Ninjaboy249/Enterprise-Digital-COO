# Google Gemini Integration Guide - Enterprise Digital COO

**Version**: 1.0  
**Last Updated**: 2026-06-24  
**Status**: Production Ready  
**Date**: 2026-06-24
**Author**: Enterprise Digital COO Team
**Model**: Gemini Pro

---

## Overview

This guide provides complete Google Gemini integration specifications for the Enterprise Digital COO, replacing OpenAI with Google's Gemini API for all AI/ML operations including reasoning, analysis, and embeddings.

## Table of Contents

1. [API Configuration](#api-configuration)
2. [Model Selection](#model-selection)
3. [Agent Integration](#agent-integration)
4. [Embeddings](#embeddings)
5. [Best Practices](#best-practices)
6. [Migration from OpenAI](#migration-from-openai)

---

## API Configuration

### Environment Variables

```bash
# .env
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-pro
GEMINI_EMBEDDING_MODEL=models/embedding-001
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2000
```

### Configuration Class

```python
# config.py
class Settings(BaseSettings):
    # Google Gemini
    GEMINI_API_KEY: str = "your-gemini-api-key"
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 2000
```

---

## Model Selection

### Available Models

1. **gemini-pro**: Best for text generation and reasoning
   - Max tokens: 32,768 input, 8,192 output
   - Best for: Complex analysis, decision making
   
2. **gemini-pro-vision**: For multimodal tasks
   - Supports: Text + Images
   - Use case: Document analysis with images

3. **models/embedding-001**: For embeddings
   - Dimensions: 768
   - Use case: Vector search, semantic similarity

---

## Agent Integration

### Base Agent Implementation

```python
import google.generativeai as genai
from config import settings

class BaseAgent:
    def __init__(self, agent_name: str, domain: str):
        self.agent_name = agent_name
        self.domain = domain
        
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def _generate_insights(self, prompt: str) -> str:
        """Generate insights using Gemini"""
        response = await self.model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=settings.GEMINI_TEMPERATURE,
                max_output_tokens=settings.GEMINI_MAX_TOKENS
            )
        )
        return response.text
```

### JSON Response Handling

Gemini doesn't have native JSON mode, so we extract JSON from responses:

```python
import json
import re

def extract_json_from_response(text: str) -> dict:
    """Extract JSON from Gemini response"""
    # Try to find JSON in response
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return {}

# Usage
response = await model.generate_content_async(
    f"{prompt}\n\nProvide your response in JSON format."
)
data = extract_json_from_response(response.text)
```

---

## Embeddings

### Using Gemini Embeddings

```python
import google.generativeai as genai

# Configure
genai.configure(api_key=settings.GEMINI_API_KEY)

# Generate embedding
result = genai.embed_content(
    model=settings.GEMINI_EMBEDDING_MODEL,
    content="Your text here",
    task_type="retrieval_document"
)
embedding = result['embedding']
```

### ChromaDB Integration

For ChromaDB, we use the default sentence-transformers embedding function as it works offline and is compatible:

```python
from chromadb.utils import embedding_functions

# Use default embedding function
embedding_function = embedding_functions.DefaultEmbeddingFunction()
```

---

## Best Practices

### 1. Prompt Engineering

Gemini responds well to clear, structured prompts:

```python
prompt = f"""
You are an expert {domain} analyst.

Task: Analyze the following data and provide insights.

Data:
{data}

Requirements:
- Provide 3-5 key insights
- Focus on actionable recommendations
- Format as bullet points

Output your response in JSON format with an 'insights' array.
"""
```

### 2. Error Handling

```python
async def call_gemini_with_retry(prompt: str, max_retries: int = 3):
    """Call Gemini with retry logic"""
    for attempt in range(max_retries):
        try:
            response = await model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 3. Rate Limiting

Gemini has rate limits. Implement throttling:

```python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = []
    
    async def acquire(self):
        now = datetime.now()
        # Remove old requests
        self.requests = [r for r in self.requests 
                        if now - r < timedelta(minutes=1)]
        
        if len(self.requests) >= self.requests_per_minute:
            wait_time = 60 - (now - self.requests[0]).seconds
            await asyncio.sleep(wait_time)
        
        self.requests.append(now)
```

### 4. Cost Optimization

- Use appropriate temperature (0.3-0.7 for analysis)
- Limit max_output_tokens to what you need
- Cache responses when possible
- Batch similar requests

---

## Migration from OpenAI

### Key Differences

| Feature | OpenAI | Gemini |
|---------|--------|--------|
| Chat API | `chat.completions.create()` | `generate_content_async()` |
| Messages | Separate system/user messages | Combined prompt |
| JSON Mode | Native `response_format` | Extract from text |
| Embeddings | `embeddings.create()` | `embed_content()` |
| Dimensions | 1536 (ada-002) | 768 (embedding-001) |

### Code Migration Examples

**Before (OpenAI):**
```python
response = await client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an expert."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7
)
text = response.choices[0].message.content
```

**After (Gemini):**
```python
full_prompt = f"You are an expert.\n\n{prompt}"
response = await model.generate_content_async(
    full_prompt,
    generation_config=genai.types.GenerationConfig(
        temperature=0.7
    )
)
text = response.text
```

---

## Testing

### Test Script

```python
# backend/test_gemini.py
import google.generativeai as genai
from config import settings

def test_gemini_api():
    """Test Gemini API connectivity"""
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    # Test generation
    response = model.generate_content("Hello, Gemini!")
    print(f"Response: {response.text}")
    
    # Test embeddings
    result = genai.embed_content(
        model=settings.GEMINI_EMBEDDING_MODEL,
        content="Test sentence",
        task_type="retrieval_document"
    )
    print(f"Embedding dimensions: {len(result['embedding'])}")

if __name__ == "__main__":
    test_gemini_api()
```

---

## Troubleshooting

### Common Issues

1. **API Key Error**
   ```bash
   # Verify API key is set
   echo $GEMINI_API_KEY
   ```

2. **Rate Limit Exceeded**
   - Implement exponential backoff
   - Reduce request frequency
   - Consider upgrading API tier

3. **JSON Parsing Errors**
   - Add explicit JSON format instruction in prompt
   - Use regex extraction with fallback
   - Validate JSON structure

---

## Summary

This guide provides production-ready Gemini integration for the Enterprise Digital COO with:

- ✅ Complete API configuration
- ✅ Agent integration patterns
- ✅ Embedding strategies
- ✅ Error handling and retry logic
- ✅ Migration guide from OpenAI
- ✅ Best practices and optimization

**Status**: Ready for production deployment with Gemini Pro

---

**Made with Codex**