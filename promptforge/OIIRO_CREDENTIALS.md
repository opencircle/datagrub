# Oiiro Account Credentials

## User Account

The Oiiro user account has been created in PromptForge:

```
Email:        rohit.iyer@oiiro.com
Password:     Welcome123
Organization: Oiiro
Role:         ADMIN
```

## Quick Setup: OpenAI API Key

### Option 1: Using the Automated Script

```bash
./setup_openai_for_oiiro.sh YOUR_OPENAI_API_KEY
```

Or run without arguments and it will prompt you:
```bash
./setup_openai_for_oiiro.sh
```

This script will:
1. ✅ Login with Oiiro credentials
2. ✅ Create/update OpenAI configuration
3. ✅ Encrypt and store the API key
4. ✅ Test the connection
5. ✅ Display the configuration

---

### Option 2: Manual API Calls

**Step 1 - Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "rohit.iyer@oiiro.com",
    "password": "Welcome123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

**Step 2 - Create OpenAI Configuration:**
```bash
curl -X POST http://localhost:8000/api/v1/model-providers/configs \
  -H "Authorization: Bearer <ACCESS_TOKEN_FROM_STEP_1>" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_name": "openai",
    "provider_type": "llm",
    "display_name": "Oiiro OpenAI Production",
    "api_key": "sk-proj-YOUR-OPENAI-KEY",
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

**Step 3 - Verify:**
```bash
curl -X GET http://localhost:8000/api/v1/model-providers/configs \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  | python3 -m json.tool
```

---

### Option 3: Python Code

```python
import requests

# Configuration
API_URL = "http://localhost:8000/api/v1"
EMAIL = "rohit.iyer@oiiro.com"
PASSWORD = "Welcome123"
OPENAI_API_KEY = "sk-proj-YOUR-KEY"

# Step 1: Login
auth_response = requests.post(f"{API_URL}/auth/login", json={
    "email": EMAIL,
    "password": PASSWORD
})
token = auth_response.json()["access_token"]

# Step 2: Create OpenAI Config
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
print(f"✅ Configuration created!")
print(f"   ID: {config['id']}")
print(f"   Masked Key: {config['api_key_masked']}")

# Step 3: Test connection
test_response = requests.post(
    f"{API_URL}/model-providers/configs/{config['id']}/test",
    headers=headers,
    json={"test_model": "gpt-3.5-turbo"}
)

if test_response.json()["success"]:
    print("✅ OpenAI connection successful!")
else:
    print("⚠️  Connection test failed (may need valid API key)")
```

---

## Expected Result

After successful setup, you'll see:

```json
{
  "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "organization_id": "737fd550-d26f-4507-8a14-568a289adea6",
  "project_id": null,
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
- ✅ API key is **encrypted** in the database
- ✅ Only **masked** version returned (`sk-proj-...xyz`)
- ✅ Scoped to **Oiiro organization**
- ✅ Ready for use in **all evaluations**

---

## Common Operations

### View Current Configuration
```bash
curl -X GET http://localhost:8000/api/v1/model-providers/configs \
  -H "Authorization: Bearer <TOKEN>" \
  | python3 -m json.tool
```

### Update Configuration
```bash
curl -X PUT http://localhost:8000/api/v1/model-providers/configs/<CONFIG_ID> \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "default_model": "gpt-4o",
      "max_tokens": 8192
    }
  }'
```

### Rotate API Key
```bash
curl -X PUT http://localhost:8000/api/v1/model-providers/configs/<CONFIG_ID> \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "NEW_OPENAI_KEY"
  }'
```

### Test Connection
```bash
curl -X POST http://localhost:8000/api/v1/model-providers/configs/<CONFIG_ID>/test \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"test_model": "gpt-3.5-turbo"}'
```

---

## API Documentation

Interactive API documentation available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Look for the `model-providers` section to explore all available endpoints.

---

## Security Notes

- ✅ Passwords are hashed with bcrypt
- ✅ API keys are encrypted with Fernet (AES-128)
- ✅ JWT tokens for authentication
- ✅ Multi-tenant isolation by organization
- ✅ API keys never returned in plaintext

---

## Troubleshooting

### "Incorrect email or password"
- The user account needs to be created first
- Run: `docker exec promptforge-api bash -c "cd /app && PYTHONPATH=/app python /app/../database-tier/seeds/create_oiiro_user.py"`

### "Could not validate credentials"
- Your JWT token expired (expires after 30 days)
- Login again to get a fresh token

### "Provider 'openai' already exists"
- A configuration already exists for OpenAI
- Use the update endpoint (PUT) instead of create (POST)
- Or delete the existing one and create a new one

---

## Database IDs (for reference)

- **Organization ID:** 737fd550-d26f-4507-8a14-568a289adea6
- **User ID:** acf7f7dc-abdd-433e-bb20-aa211d5bacc0

These are the UUIDs created for the Oiiro organization and user account.
