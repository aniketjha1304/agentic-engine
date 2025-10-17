# 📡 API Examples

Complete API examples with curl and Python requests.

## Authentication

All endpoints require API key authentication via header:
```bash
X-API-Key: your_api_key_here
```

---

## 🤖 Agents API

### Create Agent

**Request:**
```bash
curl -X POST "http://localhost:8000/agents" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "customer_support",
    "system_prompt": "You are a helpful customer support agent. Be polite and professional.",
    "workflow_names": [],
    "llm_config": {}
  }'
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/agents",
    headers={"X-API-Key": "your_api_key"},
    json={
        "name": "customer_support",
        "system_prompt": "You are a helpful customer support agent.",
        "workflow_names": [],
        "llm_config": {}
    }
)
print(response.json())
```

**Response:**
```json
{
  "name": "customer_support",
  "system_prompt": "You are a helpful customer support agent. Be polite and professional.",
  "workflow_names": [],
  "llm_config": {},
  "created_at": "2025-10-17T10:30:00",
  "updated_at": "2025-10-17T10:30:00"
}
```

### List All Agents

**Request:**
```bash
curl -X GET "http://localhost:8000/agents" \
  -H "X-API-Key: your_api_key"
```

**Response:**
```json
[
  {
    "name": "customer_support",
    "system_prompt": "You are a helpful customer support agent.",
    "workflow_names": ["handle_refund"],
    "created_at": "2025-10-17T10:30:00",
    "updated_at": "2025-10-17T10:30:00"
  },
  {
    "name": "sales_assistant",
    "system_prompt": "You are a sales assistant.",
    "workflow_names": ["check_inventory", "create_order"],
    "created_at": "2025-10-17T11:00:00",
    "updated_at": "2025-10-17T11:00:00"
  }
]
```

### Get Agent Details

**Request:**
```bash
curl -X GET "http://localhost:8000/agents/customer_support" \
  -H "X-API-Key: your_api_key"
```

**Response:**
```json
{
  "agent": {
    "name": "customer_support",
    "system_prompt": "You are a helpful customer support agent.",
    "workflow_names": ["handle_refund"],
    "created_at": "2025-10-17T10:30:00",
    "updated_at": "2025-10-17T10:30:00"
  },
  "workflows": [
    {
      "name": "handle_refund",
      "description": "Process customer refund requests",
      "status": "active",
      "code": "def handle_refund(order_id): ..."
    }
  ]
}
```

### Update Agent

**Request:**
```bash
curl -X PUT "http://localhost:8000/agents/customer_support" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "system_prompt": "You are an expert customer support agent with 10 years experience.",
    "workflow_names": ["handle_refund", "check_order_status"]
  }'
```

**Response:**
```json
{
  "name": "customer_support",
  "system_prompt": "You are an expert customer support agent with 10 years experience.",
  "workflow_names": ["handle_refund", "check_order_status"],
  "updated_at": "2025-10-17T12:00:00"
}
```

### Delete Agent

**Request:**
```bash
curl -X DELETE "http://localhost:8000/agents/customer_support" \
  -H "X-API-Key: your_api_key"
```

**Response:** `204 No Content`

---

## ⚙️ Workflows API

### Create Workflow

**Request:**
```bash
curl -X POST "http://localhost:8000/workflows" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "send_email",
    "code": "def send_email(to, subject, body):\n    # Send email logic\n    return {\"status\": \"sent\"}",
    "status": "active",
    "description": "Send an email to a recipient",
    "endpoint": "/execute/send_email",
    "attributes": {
      "category": "communication",
      "requires_auth": true
    }
  }'
```

**Python:**
```python
workflow_code = '''
def send_email(to, subject, body):
    # Send email logic
    return {"status": "sent"}
'''

response = requests.post(
    "http://localhost:8000/workflows",
    headers={"X-API-Key": "your_api_key"},
    json={
        "name": "send_email",
        "code": workflow_code,
        "status": "active",
        "description": "Send an email to a recipient",
        "attributes": {"category": "communication"}
    }
)
```

**Response:**
```json
{
  "name": "send_email",
  "code": "def send_email(to, subject, body):\n    ...",
  "status": "active",
  "endpoint": "/execute/send_email",
  "attributes": {
    "category": "communication",
    "requires_auth": true
  },
  "description": "Send an email to a recipient",
  "created_at": "2025-10-17T10:30:00",
  "updated_at": "2025-10-17T10:30:00"
}
```

### List All Workflows

**Request:**
```bash
curl -X GET "http://localhost:8000/workflows" \
  -H "X-API-Key: your_api_key"
```

### Get Workflow

**Request:**
```bash
curl -X GET "http://localhost:8000/workflows/send_email" \
  -H "X-API-Key: your_api_key"
```

### Update Workflow

**Request:**
```bash
curl -X PUT "http://localhost:8000/workflows/send_email" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "inactive",
    "description": "Updated: Send an email to a recipient"
  }'
```

### Delete Workflow

**Request:**
```bash
curl -X DELETE "http://localhost:8000/workflows/send_email" \
  -H "X-API-Key: your_api_key"
```

---

## 💬 Chats API

### Create Chat

**Request:**
```bash
curl -X POST "http://localhost:8000/chats" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Support Chat - John Doe",
    "agent_name": "customer_support"
  }'
```

**Python:**
```python
response = requests.post(
    "http://localhost:8000/chats",
    headers={"X-API-Key": "your_api_key"},
    json={
        "name": "Customer Support Chat - John Doe",
        "agent_name": "customer_support"
    }
)
chat_id = response.json()["id"]
print(f"Created chat: {chat_id}")
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Customer Support Chat - John Doe",
  "agent_name": "customer_support",
  "created_at": "2025-10-17T10:30:00",
  "updated_at": "2025-10-17T10:30:00",
  "messages": []
}
```

### List All Chats

**Request:**
```bash
curl -X GET "http://localhost:8000/chats" \
  -H "X-API-Key: your_api_key"
```

### Get Chat with Messages

**Request:**
```bash
curl -X GET "http://localhost:8000/chats/550e8400-e29b-41d4-a716-446655440000" \
  -H "X-API-Key: your_api_key"
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Customer Support Chat - John Doe",
  "agent_name": "customer_support",
  "created_at": "2025-10-17T10:30:00",
  "updated_at": "2025-10-17T10:35:00",
  "messages": [
    {
      "role": "user",
      "content": "I need help with my order",
      "timestamp": "2025-10-17T10:31:00"
    },
    {
      "role": "assistant",
      "content": "I'd be happy to help you with your order. Could you please provide your order number?",
      "timestamp": "2025-10-17T10:31:05"
    }
  ]
}
```

### Update Chat

**Request:**
```bash
curl -X PUT "http://localhost:8000/chats/550e8400-e29b-41d4-a716-446655440000?name=Updated%20Chat%20Name" \
  -H "X-API-Key: your_api_key"
```

### Delete Chat

**Request:**
```bash
curl -X DELETE "http://localhost:8000/chats/550e8400-e29b-41d4-a716-446655440000" \
  -H "X-API-Key: your_api_key"
```

---

## 💭 Chat Agent API (Main Endpoint)

### Send Message to Agent

**Request:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "550e8400-e29b-41d4-a716-446655440000",
    "agent_name": "customer_support",
    "message": "I need help with my order #12345"
  }'
```

**Python:**
```python
response = requests.post(
    "http://localhost:8000/chat",
    headers={"X-API-Key": "your_api_key"},
    json={
        "chat_id": "550e8400-e29b-41d4-a716-446655440000",
        "agent_name": "customer_support",
        "message": "I need help with my order #12345"
    }
)
print(response.json()["message"])
```

**Response:**
```json
{
  "message": "I'd be happy to help you with order #12345. Let me check the status for you. Could you please confirm your email address associated with this order?",
  "chat_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 🔄 Complete Conversation Flow Example

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000"
API_KEY = "your_api_key"
headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# 1. Create an agent
print("Creating agent...")
agent_response = requests.post(
    f"{BASE_URL}/agents",
    headers=headers,
    json={
        "name": "helpful_assistant",
        "system_prompt": "You are a helpful AI assistant.",
        "workflow_names": []
    }
)
print(f"✓ Agent created: {agent_response.json()['name']}")

# 2. Create a chat
print("\nCreating chat...")
chat_response = requests.post(
    f"{BASE_URL}/chats",
    headers=headers,
    json={
        "name": "My Conversation",
        "agent_name": "helpful_assistant"
    }
)
chat_id = chat_response.json()["id"]
print(f"✓ Chat created: {chat_id}")

# 3. Have a conversation
print("\nStarting conversation...")
messages = [
    "Hello! What can you help me with?",
    "Can you explain what you do?",
    "That's great! Thanks for the help."
]

for user_message in messages:
    print(f"\nUser: {user_message}")
    
    response = requests.post(
        f"{BASE_URL}/chat",
        headers=headers,
        json={
            "chat_id": chat_id,
            "agent_name": "helpful_assistant",
            "message": user_message
        }
    )
    
    assistant_message = response.json()["message"]
    print(f"Assistant: {assistant_message}")

# 4. Retrieve full chat history
print("\n\nRetrieving full conversation...")
history_response = requests.get(
    f"{BASE_URL}/chats/{chat_id}",
    headers=headers
)
chat_data = history_response.json()
print(f"\nTotal messages: {len(chat_data['messages'])}")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';
const API_KEY = 'your_api_key';
const headers = {
  'X-API-Key': API_KEY,
  'Content-Type': 'application/json'
};

async function runConversation() {
  try {
    // 1. Create agent
    const agentRes = await axios.post(
      `${BASE_URL}/agents`,
      {
        name: 'helpful_assistant',
        system_prompt: 'You are a helpful AI assistant.',
        workflow_names: []
      },
      { headers }
    );
    console.log('Agent created:', agentRes.data.name);

    // 2. Create chat
    const chatRes = await axios.post(
      `${BASE_URL}/chats`,
      {
        name: 'My Conversation',
        agent_name: 'helpful_assistant'
      },
      { headers }
    );
    const chatId = chatRes.data.id;
    console.log('Chat created:', chatId);

    // 3. Send message
    const messageRes = await axios.post(
      `${BASE_URL}/chat`,
      {
        chat_id: chatId,
        agent_name: 'helpful_assistant',
        message: 'Hello! How can you help me?'
      },
      { headers }
    );
    console.log('Assistant:', messageRes.data.message);

  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

runConversation();
```

---

## 🧪 Testing Endpoints

### Health Check

**Request:**
```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "ok",
  "message": "Agentic Engine is healthy and running",
  "version": "2.0.0"
}
```

### Root Endpoint

**Request:**
```bash
curl -X GET "http://localhost:8000/"
```

**Response:**
```json
{
  "name": "Agentic Engine",
  "version": "2.0.0",
  "description": "Multi-agent platform with dynamic workflow orchestration",
  "docs": "/docs"
}
```

---

## 📊 Error Responses

### 400 Bad Request
```json
{
  "detail": "Agent with name 'customer_support' already exists"
}
```

### 404 Not Found
```json
{
  "detail": "Agent 'nonexistent_agent' not found"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid API Key"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to process message. Please try again later."
}
```

---

## 🔐 Authentication Examples

### Using curl
```bash
# Correct
curl -H "X-API-Key: your_key" ...

# Wrong
curl -H "Authorization: Bearer your_key" ...  # ❌ Not supported
```

### Using Python requests
```python
# Correct
headers = {"X-API-Key": "your_key"}
requests.get(url, headers=headers)

# Wrong
headers = {"Authorization": "Bearer your_key"}  # ❌ Not supported
```

### Using JavaScript fetch
```javascript
// Correct
fetch(url, {
  headers: {
    'X-API-Key': 'your_key'
  }
})
```

---

## 💡 Best Practices

1. **Store chat_id**: Save the chat ID after creation for subsequent messages
2. **Agent names**: Use descriptive, unique names (lowercase with underscores)
3. **Error handling**: Always check response status codes
4. **Rate limiting**: Consider implementing delays between requests in production
5. **Message history**: Retrieve full chat history periodically for UI sync

---

## 📝 Notes

- All timestamps are in UTC
- Chat IDs are UUIDs (automatically generated)
- Agent and workflow names are case-sensitive unique identifiers
- Message history is unlimited (consider pagination in future)

