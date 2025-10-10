# Quick Start: Setup OpenAI for Oiiro

## Option 1: Use the Setup Script (Easiest)

```bash
./setup_oiiro_openai.sh <your-email> <your-password> <openai-api-key>
```

**Example:**
```bash
./setup_oiiro_openai.sh admin@promptforge.com mypassword sk-proj-abc123...
```

Or without API key (will prompt you):
```bash
./setup_oiiro_openai.sh admin@promptforge.com mypassword
```

---

## Option 2: Manual cURL Commands

### 1. Login and get token:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@promptforge.com",
    "password": "password"
  }'
```

Save the `access_token` from response.

### 2. Create OpenAI configuration:
```bash
curl -X POST http://localhost:8000/api/v1/model-providers/configs \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_name": "openai",
    "provider_type": "llm",
    "display_name": "Oiiro OpenAI Production",
    "api_key": "YOUR_OPENAI_API_KEY",
    "config": {
      "organization_id": "org-oiiro",
      "default_model": "gpt-4-turbo",
      "max_tokens": 4096,
      "temperature": 0.7
    },
    "is_active": true,
    "is_default": true,
    "project_id": null
  }'
```

### 3. Verify configuration:
```bash
curl -X GET http://localhost:8000/api/v1/model-providers/configs \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  | python3 -m json.tool
```

---

## Option 3: Using Python

```python
import requests

# Configuration
API_URL = "http://localhost:8000/api/v1"
EMAIL = "admin@promptforge.com"
PASSWORD = "password"
OPENAI_API_KEY = "sk-proj-abc123..."

# Step 1: Login
response = requests.post(f"{API_URL}/auth/login", json={
    "email": EMAIL,
    "password": PASSWORD
})
token = response.json()["access_token"]

# Step 2: Create OpenAI configuration
headers = {"Authorization": f"Bearer {token}"}
config_data = {
    "provider_name": "openai",
    "provider_type": "llm",
    "display_name": "Oiiro OpenAI Production",
    "api_key": OPENAI_API_KEY,
    "config": {
        "organization_id": "org-oiiro",
        "default_model": "gpt-4-turbo",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "is_active": True,
    "is_default": True,
    "project_id": None
}

response = requests.post(
    f"{API_URL}/model-providers/configs",
    headers=headers,
    json=config_data
)

config = response.json()
print(f"✅ Configuration created: {config['id']}")
print(f"   API Key (masked): {config['api_key_masked']}")

# Step 3: Verify
response = requests.get(
    f"{API_URL}/model-providers/configs/{config['id']}",
    headers=headers
)
print("\n📋 Configuration details:")
print(response.json())
```

---

## What You'll Get

After successful setup, you'll see:

```json
{
  "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "organization_id": "org-123...",
  "provider_name": "openai",
  "provider_type": "llm",
  "display_name": "Oiiro OpenAI Production",
  "api_key_masked": "sk-proj-...xyz",
  "config": {
    "organization_id": "org-oiiro",
    "default_model": "gpt-4-turbo",
    "max_tokens": 4096,
    "temperature": 0.7
  },
  "is_active": true,
  "is_default": true,
  "usage_count": 0,
  "created_at": "2025-10-05T18:30:00Z"
}
```

**Key Points:**
- ✅ API key is **encrypted** in database
- ✅ Only **masked** key returned (`sk-proj-...xyz`)
- ✅ Available for all Oiiro organization users
- ✅ Ready for use in evaluations

---

## Common Operations

### Update configuration:
```bash
curl -X PUT http://localhost:8000/api/v1/model-providers/configs/CONFIG_ID \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"config": {"max_tokens": 8192}}'
```

### Rotate API key:
```bash
curl -X PUT http://localhost:8000/api/v1/model-providers/configs/CONFIG_ID \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "NEW_OPENAI_KEY"}'
```

### Test connection:
```bash
curl -X POST http://localhost:8000/api/v1/model-providers/configs/CONFIG_ID/test \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"test_model": "gpt-3.5-turbo"}'
```

### Delete configuration:
```bash
curl -X DELETE http://localhost:8000/api/v1/model-providers/configs/CONFIG_ID \
  -H "Authorization: Bearer TOKEN"
```

---

## Troubleshooting

**"Could not validate credentials"**
- Your token expired or is invalid
- Login again to get a fresh token

**"Provider 'openai' already exists"**
- Configuration already exists
- Use GET to retrieve it, or PUT to update it

**"Provider 'openai' not found"**
- Run metadata seeding:
  ```bash
  docker exec promptforge-api bash -c "cd /app && PYTHONPATH=/app python scripts/seed_model_providers.py"
  ```

---

## Next Steps

Once configured, the OpenAI API key will be automatically used in:
- LLM Judge evaluations
- Custom evaluations
- Any PromptForge feature requiring OpenAI

No need to set environment variables anymore! 🎉
