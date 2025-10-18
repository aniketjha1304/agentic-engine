# API Documentation

**Base URL:** `http://localhost:8000`

**Authentication:** All endpoints require authentication via header:
- `X-API-Key: your_api_key` OR
- `Authorization: Bearer your_api_key`

---

## Agents API

### Create Agent
**POST** `/agents`

**Request:**
```json
{
  "name": "my_assistant",
  "system_prompt": "You are a helpful AI assistant.",
  "workflow_names": ["workflow1", "workflow2"],
  "llm_config": {}
}
```

**Response:** `201 Created`
```json
{
  "name": "my_assistant",
  "system_prompt": "You are a helpful AI assistant.",
  "workflow_names": ["workflow1", "workflow2"],
  "llm_config": {},
  "created_at": "2025-10-18T10:30:00",
  "updated_at": "2025-10-18T10:30:00"
}
```

---

### Get All Agents
**GET** `/agents`

**Response:** `200 OK`
```json
[
  {
    "name": "my_assistant",
    "system_prompt": "You are a helpful AI assistant.",
    "workflow_names": ["workflow1"],
    "llm_config": {},
    "created_at": "2025-10-18T10:30:00",
    "updated_at": "2025-10-18T10:30:00"
  }
]
```

---

### Get Agent by Name
**GET** `/agents/{agent_name}`

**Response:** `200 OK`
```json
{
  "agent": {
    "name": "my_assistant",
    "system_prompt": "You are a helpful AI assistant.",
    "workflow_names": ["send_email"],
    "llm_config": {},
    "created_at": "2025-10-18T10:30:00",
    "updated_at": "2025-10-18T10:30:00"
  },
  "workflows": [
    {
      "name": "send_email",
      "code": "def send_email(to, subject, body): ...",
      "status": "active",
      "endpoint": "/execute/send_email",
      "attributes": {},
      "description": "Send an email to a recipient",
      "input_parameters": {
        "type": "object",
        "properties": {
          "to": {"type": "string"},
          "subject": {"type": "string"},
          "body": {"type": "string"}
        }
      },
      "created_at": "2025-10-18T10:00:00",
      "updated_at": "2025-10-18T10:00:00"
    }
  ]
}
```

---

### Update Agent
**PUT** `/agents/{agent_name}`

**Request:** (all fields optional)
```json
{
  "system_prompt": "Updated system prompt",
  "workflow_names": ["workflow1", "workflow2"],
  "llm_config": {"temperature": 0.7}
}
```

**Response:** `200 OK`
```json
{
  "name": "my_assistant",
  "system_prompt": "Updated system prompt",
  "workflow_names": ["workflow1", "workflow2"],
  "llm_config": {"temperature": 0.7},
  "created_at": "2025-10-18T10:30:00",
  "updated_at": "2025-10-18T12:00:00"
}
```

---

### Delete Agent
**DELETE** `/agents/{agent_name}`

**Response:** `204 No Content`

---

## Workflows API

### Create Workflow
**POST** `/workflows`

**Request:**
```json
{
  "name": "send_email",
  "code": "def send_email(to, subject, body):\n    return {'status': 'sent'}",
  "status": "active",
  "endpoint": "http://workflow-service.com/send_email",
  "attributes": {"category": "communication"},
  "description": "Send an email to a recipient",
  "input_parameters": {
    "type": "object",
    "properties": {
      "to": {"type": "string", "format": "email"},
      "subject": {"type": "string"},
      "body": {"type": "string"}
    },
    "required": ["to", "subject", "body"]
  }
}
```

**Response:** `201 Created`
```json
{
  "name": "send_email",
  "code": "def send_email(to, subject, body):\n    return {'status': 'sent'}",
  "status": "active",
  "endpoint": "http://workflow-service.com/send_email",
  "attributes": {"category": "communication"},
  "description": "Send an email to a recipient",
  "input_parameters": {
    "type": "object",
    "properties": {
      "to": {"type": "string", "format": "email"},
      "subject": {"type": "string"},
      "body": {"type": "string"}
    },
    "required": ["to", "subject", "body"]
  },
  "created_at": "2025-10-18T10:30:00",
  "updated_at": "2025-10-18T10:30:00"
}
```

---

### Get All Workflows
**GET** `/workflows`

**Response:** `200 OK`
```json
[
  {
    "name": "send_email",
    "code": "def send_email(to, subject, body):\n    return {'status': 'sent'}",
    "status": "active",
    "endpoint": "http://workflow-service.com/send_email",
    "attributes": {"category": "communication"},
    "description": "Send an email to a recipient",
    "input_parameters": {
      "type": "object",
      "properties": {
        "to": {"type": "string"},
        "subject": {"type": "string"},
        "body": {"type": "string"}
      }
    },
    "created_at": "2025-10-18T10:30:00",
    "updated_at": "2025-10-18T10:30:00"
  }
]
```

---

### Get Workflow by Name
**GET** `/workflows/{workflow_name}`

**Response:** `200 OK`
```json
{
  "name": "send_email",
  "code": "def send_email(to, subject, body):\n    return {'status': 'sent'}",
  "status": "active",
  "endpoint": "http://workflow-service.com/send_email",
  "attributes": {"category": "communication"},
  "description": "Send an email to a recipient",
  "input_parameters": {
    "type": "object",
    "properties": {
      "to": {"type": "string"},
      "subject": {"type": "string"},
      "body": {"type": "string"}
    }
  },
  "created_at": "2025-10-18T10:30:00",
  "updated_at": "2025-10-18T10:30:00"
}
```

---

### Update Workflow
**PUT** `/workflows/{workflow_name}`

**Request:** (all fields optional)
```json
{
  "code": "def send_email(to, subject, body):\n    # Updated code\n    return {'status': 'sent'}",
  "status": "inactive",
  "endpoint": "http://new-service.com/send_email",
  "attributes": {"category": "communication", "priority": "high"},
  "description": "Updated description",
  "input_parameters": {
    "type": "object",
    "properties": {
      "to": {"type": "string"},
      "subject": {"type": "string"},
      "body": {"type": "string"}
    }
  }
}
```

**Response:** `200 OK`
```json
{
  "name": "send_email",
  "code": "def send_email(to, subject, body):\n    # Updated code\n    return {'status': 'sent'}",
  "status": "inactive",
  "endpoint": "http://new-service.com/send_email",
  "attributes": {"category": "communication", "priority": "high"},
  "description": "Updated description",
  "input_parameters": {
    "type": "object",
    "properties": {
      "to": {"type": "string"},
      "subject": {"type": "string"},
      "body": {"type": "string"}
    }
  },
  "created_at": "2025-10-18T10:30:00",
  "updated_at": "2025-10-18T12:00:00"
}
```

---

### Delete Workflow
**DELETE** `/workflows/{workflow_name}`

**Response:** `204 No Content`

---

### Execute Workflow
**POST** `/workflows/{workflow_name}/execute`

**Request:**
```json
{
  "workflow_name": "send_email",
  "input_data": {
    "to": "user@example.com",
    "subject": "Hello",
    "body": "This is a test email"
  }
}
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "workflow_name": "send_email",
  "result": {
    "status": "sent",
    "message_id": "12345"
  }
}
```

---

## Chats API

### Create Chat
**POST** `/chats`

**Request:**
```json
{
  "name": "Customer Support Chat",
  "agent_name": "my_assistant"
}
```

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Customer Support Chat",
  "agent_name": "my_assistant",
  "created_at": "2025-10-18T10:30:00",
  "updated_at": "2025-10-18T10:30:00",
  "messages": []
}
```

---

### Get All Chats
**GET** `/chats`

**Response:** `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Customer Support Chat",
    "agent_name": "my_assistant",
    "created_at": "2025-10-18T10:30:00",
    "updated_at": "2025-10-18T10:35:00",
    "messages": [
      {
        "role": "user",
        "content": "Hello",
        "timestamp": "2025-10-18T10:31:00"
      },
      {
        "role": "assistant",
        "content": "Hi! How can I help you?",
        "timestamp": "2025-10-18T10:31:05"
      }
    ]
  }
]
```

---

### Get Chat by ID
**GET** `/chats/{chat_id}`

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Customer Support Chat",
  "agent_name": "my_assistant",
  "created_at": "2025-10-18T10:30:00",
  "updated_at": "2025-10-18T10:35:00",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2025-10-18T10:31:00"
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help you?",
      "timestamp": "2025-10-18T10:31:05"
    }
  ]
}
```

---

### Update Chat
**PUT** `/chats/{chat_id}?name=New%20Chat%20Name&agent_name=new_agent`

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "New Chat Name",
  "agent_name": "new_agent",
  "created_at": "2025-10-18T10:30:00",
  "updated_at": "2025-10-18T12:00:00",
  "messages": []
}
```

---

### Delete Chat
**DELETE** `/chats/{chat_id}`

**Response:** `204 No Content`

---

### Send Message to Agent
**POST** `/chat`

**Request:**
```json
{
  "chat_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_name": "my_assistant",
  "message": "What can you help me with?"
}
```

**Response:** `200 OK`
```json
{
  "message": "I can help you with various tasks including executing workflows, answering questions, and more. I have access to tools like get_workflow_details and execute_workflow.",
  "chat_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Agent with name 'my_assistant' already exists"
}
```

### 401 Unauthorized
```json
{
  "detail": "API key is missing or invalid. Provide either X-API-Key header or Authorization: Bearer token"
}
```

### 404 Not Found
```json
{
  "detail": "Agent 'nonexistent_agent' not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to process message. Please try again later."
}
```
