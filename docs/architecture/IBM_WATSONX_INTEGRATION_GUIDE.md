# IBM watsonx.ai Integration Guide - Enterprise Digital COO

**Version**: 1.0  
**Last Updated**: 2026-06-24  
**Status**: Production Ready  
**Author**: Enterprise Digital COO Team
**Model**: IBM Granite 13B Chat v2

---

## Overview

This guide provides complete IBM watsonx.ai integration specifications for the Enterprise Digital COO. IBM watsonx.ai is IBM's enterprise-grade AI platform that provides foundation models for text generation, analysis, and reasoning.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [API Configuration](#api-configuration)
3. [Available Models](#available-models)
4. [Agent Integration](#agent-integration)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### IBM Cloud Account Setup

1. **Create IBM Cloud Account**: https://cloud.ibm.com/registration
2. **Create watsonx.ai Project**:
   - Navigate to watsonx.ai service
   - Create a new project
   - Note your Project ID

3. **Get API Key**:
   - Go to IBM Cloud Dashboard
   - Navigate to "Manage" → "Access (IAM)" → "API keys"
   - Create a new API key
   - Save it securely

### Required Information

- **API Key**: Your IBM Cloud API key
- **Project ID**: Your watsonx.ai project ID
- **URL**: Regional endpoint (e.g., `https://us-south.ml.cloud.ibm.com`)

---

## API Configuration

### Environment Variables

```bash
# .env
WATSONX_API_KEY=your-watsonx-api-key-here
WATSONX_PROJECT_ID=your-project-id-here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL=ibm/granite-13b-chat-v2
WATSONX_TEMPERATURE=0.7
WATSONX_MAX_TOKENS=2000
WATSONX_MIN_TOKENS=50
WATSONX_DECODING_METHOD=greedy
```

### Configuration Class

```python
# config.py
class Settings(BaseSettings):
    # IBM watsonx.ai
    WATSONX_API_KEY: str = "your-watsonx-api-key"
    WATSONX_PROJECT_ID: str = "your-project-id"
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"
    WATSONX_MODEL: str = "ibm/granite-13b-chat-v2"
    WATSONX_TEMPERATURE: float = 0.7
    WATSONX_MAX_TOKENS: int = 2000
    WATSONX_MIN_TOKENS: int = 50
    WATSONX_DECODING_METHOD: str = "greedy"
```

---

## Available Models

### IBM Granite Models (Recommended)

1. **ibm/granite-13b-chat-v2**
   - Best for: Conversational AI, business analysis
   - Context length: 8,192 tokens
   - Strengths: Enterprise-focused, reliable

2. **ibm/granite-13b-instruct-v2**
   - Best for: Instruction following, structured tasks
   - Context length: 8,192 tokens
   - Strengths: Precise instruction execution

### Meta Llama Models

3. **meta-llama/llama-2-70b-chat**
   - Best for: Complex reasoning, long conversations
   - Context length: 4,096 tokens
   - Strengths: High quality responses

4. **meta-llama/llama-2-13b-chat**
   - Best for: Balanced performance and speed
   - Context length: 4,096 tokens
   - Strengths: Good for most tasks

### Regional Endpoints

- **US South**: `https://us-south.ml.cloud.ibm.com`
- **EU Germany**: `https://eu-de.ml.cloud.ibm.com`
- **Japan Tokyo**: `https://jp-tok.ml.cloud.ibm.com`

---

## Agent Integration

### Base Agent Implementation

```python
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from config import settings

class BaseAgent:
    def __init__(self, agent_name: str, domain: str):
        self.agent_name = agent_name
        self.domain = domain
        
        # Configure IBM watsonx.ai
        self.model_params = {
            GenParams.DECODING_METHOD: settings.WATSONX_DECODING_METHOD,
            GenParams.TEMPERATURE: settings.WATSONX_TEMPERATURE,
            GenParams.MAX_NEW_TOKENS: settings.WATSONX_MAX_TOKENS,
            GenParams.MIN_NEW_TOKENS: settings.WATSONX_MIN_TOKENS,
        }
        
        self.model = Model(
            model_id=settings.WATSONX_MODEL,
            params=self.model_params,
            credentials={
                "apikey": settings.WATSONX_API_KEY,
                "url": settings.WATSONX_URL
            },
            project_id=settings.WATSONX_PROJECT_ID
        )
    
    async def _generate_insights(self, prompt: str) -> str:
        """Generate insights using IBM watsonx.ai"""
        import asyncio
        
        # watsonx.ai uses synchronous API, wrap in async
        response = await asyncio.to_thread(
            self.model.generate_text,
            prompt=prompt
        )
        return response
```

### JSON Response Handling

IBM watsonx.ai doesn't have native JSON mode, so we extract JSON from responses:

```python
import json
import re

def extract_json_from_response(text: str) -> dict:
    """Extract JSON from watsonx.ai response"""
    # Try to find JSON in response
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            return {}
    return {}

# Usage
prompt = f"{your_prompt}\n\nProvide your response in JSON format."
response = await asyncio.to_thread(model.generate_text, prompt=prompt)
data = extract_json_from_response(response)
```

---

## Best Practices

### 1. Prompt Engineering

IBM Granite models respond well to clear, structured prompts:

```python
prompt = f"""
You are an expert {domain} analyst for an enterprise organization.

Task: Analyze the following data and provide actionable insights.

Data:
{data}

Requirements:
- Provide 3-5 key insights
- Focus on business impact
- Be specific and actionable
- Format as bullet points

Output your response in JSON format with an 'insights' array.
"""
```

### 2. Parameter Tuning

```python
# For creative tasks
params = {
    GenParams.DECODING_METHOD: "sample",
    GenParams.TEMPERATURE: 0.9,
    GenParams.TOP_P: 0.95,
    GenParams.TOP_K: 50,
}

# For analytical tasks (recommended)
params = {
    GenParams.DECODING_METHOD: "greedy",
    GenParams.TEMPERATURE: 0.3,
    GenParams.MAX_NEW_TOKENS: 2000,
}

# For balanced tasks
params = {
    GenParams.DECODING_METHOD: "sample",
    GenParams.TEMPERATURE: 0.7,
    GenParams.TOP_P: 0.9,
}
```

### 3. Error Handling

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_watsonx_with_retry(model, prompt: str):
    """Call watsonx.ai with retry logic"""
    try:
        response = await asyncio.to_thread(
            model.generate_text,
            prompt=prompt
        )
        return response
    except Exception as e:
        logger.error(f"watsonx.ai call failed: {e}")
        raise
```

### 4. Cost Optimization

- Use appropriate token limits
- Cache responses when possible
- Use `greedy` decoding for deterministic outputs
- Batch similar requests
- Monitor token usage

### 5. Async Wrapper

Since watsonx.ai SDK is synchronous, always wrap in async:

```python
import asyncio

async def async_generate(model, prompt: str) -> str:
    """Async wrapper for watsonx.ai generation"""
    return await asyncio.to_thread(
        model.generate_text,
        prompt=prompt
    )
```

---

## Troubleshooting

### Common Issues

#### 1. Authentication Error

```
Error: Invalid API key or project ID
```

**Solution**:
```bash
# Verify credentials
echo $WATSONX_API_KEY
echo $WATSONX_PROJECT_ID

# Test with curl
curl -X POST "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello", "model_id": "ibm/granite-13b-chat-v2", "project_id": "YOUR_PROJECT_ID"}'
```

#### 2. Model Not Found

```
Error: Model ID not found
```

**Solution**:
- Verify model ID is correct
- Check model availability in your region
- Ensure project has access to the model

#### 3. Rate Limiting

```
Error: Too many requests
```

**Solution**:
- Implement exponential backoff
- Reduce request frequency
- Consider upgrading your plan

#### 4. Timeout Errors

```
Error: Request timeout
```

**Solution**:
```python
# Increase timeout
model = Model(
    model_id=settings.WATSONX_MODEL,
    params=model_params,
    credentials=credentials,
    project_id=project_id,
    timeout=120  # Increase timeout to 120 seconds
)
```

---

## Testing

### Test Script

Run the test script to verify your setup:

```bash
python backend/test_watsonx.py
```

Expected output:
```
============================================================
IBM watsonx.ai API Test
============================================================

1. Checking API Configuration...
[OK] API Key found: abcd1234...xyz
[OK] Project ID: 12345678...abcd
[OK] URL: https://us-south.ml.cloud.ibm.com
[OK] Model: ibm/granite-13b-chat-v2

2. Initializing IBM watsonx.ai...
[OK] watsonx.ai initialized successfully

3. Testing Text Generation...
[OK] Response received
[OK] Response: Hello, IBM watsonx.ai is working!

4. Testing Complex Query...
[OK] Complex query successful

============================================================
[SUCCESS] ALL TESTS PASSED - IBM watsonx.ai is working correctly!
============================================================
```

---

## Performance Considerations

### Response Times

- **Granite 13B**: ~2-5 seconds for typical queries
- **Llama 2 70B**: ~5-10 seconds for complex queries
- **Llama 2 13B**: ~2-4 seconds for typical queries

### Token Limits

- **Input**: Up to 8,192 tokens (Granite models)
- **Output**: Configurable via `MAX_NEW_TOKENS`
- **Total**: Input + Output must be within model limits

### Concurrent Requests

- Default: 10 concurrent requests per project
- Enterprise: Contact IBM for higher limits

---

## Migration from Other Providers

### From OpenAI

| OpenAI | IBM watsonx.ai |
|--------|----------------|
| `gpt-4` | `ibm/granite-13b-chat-v2` |
| `gpt-3.5-turbo` | `meta-llama/llama-2-13b-chat` |
| `chat.completions.create()` | `model.generate_text()` |
| Async native | Wrap with `asyncio.to_thread()` |
| JSON mode | Extract with regex |

### From Google Gemini

| Gemini | IBM watsonx.ai |
|--------|----------------|
| `gemini-pro` | `ibm/granite-13b-chat-v2` |
| `generate_content_async()` | `generate_text()` + async wrapper |
| Native async | Wrap with `asyncio.to_thread()` |

---

## Summary

This guide provides production-ready IBM watsonx.ai integration for the Enterprise Digital COO with:

- ✅ Complete API configuration
- ✅ Model selection guide
- ✅ Agent integration patterns
- ✅ Best practices and optimization
- ✅ Error handling strategies
- ✅ Troubleshooting guide
- ✅ Performance considerations

**Status**: Ready for production deployment with IBM watsonx.ai

---

## Additional Resources

- **IBM watsonx.ai Documentation**: https://www.ibm.com/docs/en/watsonx-as-a-service
- **API Reference**: https://ibm.github.io/watsonx-ai-python-sdk/
- **Model Cards**: https://www.ibm.com/products/watsonx-ai/foundation-models
- **Pricing**: https://www.ibm.com/products/watsonx-ai/pricing

---

**Made with Bob**