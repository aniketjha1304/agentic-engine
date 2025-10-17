# 🤖 Agentic Engine - Refactored Backend

A simple yet powerful multi-agent platform built with FastAPI and MongoDB. Create configurable AI agents, define workflows, and chat with intelligent assistants.

## 🎯 Overview

The Agentic Engine allows you to:
- **Create Agents**: Configure AI agents with custom system prompts
- **Define Workflows**: Build reusable workflows/skills that agents can execute
- **Manage Chats**: Persistent chat sessions with full message history
- **Dynamic Agent Building**: Agents are built at runtime with their configured prompts and associated workflow descriptions

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐  ┌───────────┐  ┌────────┐  ┌──────────────┐ │
│  │  Agents  │  │ Workflows │  │ Chats  │  │  Chat Agent  │ │
│  │   API    │  │    API    │  │  API   │  │     API      │ │
│  └────┬─────┘  └─────┬─────┘  └───┬────┘  └──────┬───────┘ │
│       │              │            │                │         │
│       └──────────────┴────────────┴────────────────┘         │
│                           │                                   │
│                    ┌──────▼──────┐                           │
│                    │   Services   │                           │
│                    │  (Agent      │                           │
│                    │   Builder)   │                           │
│                    └──────┬───────┘                           │
│                           │                                   │
│                    ┌──────▼──────┐                           │
│                    │   Database   │                           │
│                    │    Queries   │                           │
│                    └──────┬───────┘                           │
└───────────────────────────┼───────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │    MongoDB     │
                    │  Collections:  │
                    │  - agents      │
                    │  - workflows   │
                    │  - chats       │
                    └────────────────┘
```

## 📦 Collections Schema

### Agents Collection
```json
{
  "name": "string (unique)",
  "system_prompt": "string",
  "workflow_names": ["workflow1", "workflow2"],
  "llm_config": {},
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Workflows Collection
```json
{
  "name": "string (unique)",
  "code": "string",
  "status": "active|inactive",
  "endpoint": "string (optional)",
  "attributes": {},
  "description": "string (optional)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Chats Collection
```json
{
  "id": "string (uuid)",
  "name": "string",
  "agent_name": "string (optional)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "messages": [
    {
      "role": "user|assistant",
      "content": "string",
      "timestamp": "datetime"
    }
  ]
}
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MongoDB (local or cloud instance)
- Azure OpenAI API access

### Installation

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start MongoDB** (if running locally)
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or use MongoDB Atlas (cloud)
```

4. **Run the application**
```bash
cd backend
uvicorn app.main_new:app --reload --port 8000
```

5. **Access the API**
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 📚 API Endpoints

### Agents
- `POST /agents` - Create a new agent
- `GET /agents` - List all agents
- `GET /agents/{agent_name}` - Get agent details with workflows
- `PUT /agents/{agent_name}` - Update agent
- `DELETE /agents/{agent_name}` - Delete agent

### Workflows
- `POST /workflows` - Create a new workflow
- `GET /workflows` - List all workflows
- `GET /workflows/{workflow_name}` - Get workflow details
- `PUT /workflows/{workflow_name}` - Update workflow
- `DELETE /workflows/{workflow_name}` - Delete workflow

### Chats
- `POST /chats` - Create a new chat
- `GET /chats` - List all chats
- `GET /chats/{chat_id}` - Get chat with messages
- `PUT /chats/{chat_id}` - Update chat
- `DELETE /chats/{chat_id}` - Delete chat

### Chat Agent
- `POST /chat` - Send message to agent (main endpoint)

## 💬 Usage Example

### 1. Create an Agent
```bash
curl -X POST "http://localhost:8000/agents" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "assistant",
    "system_prompt": "You are a helpful AI assistant.",
    "workflow_names": []
  }'
```

### 2. Create a Workflow
```bash
curl -X POST "http://localhost:8000/workflows" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_weather",
    "code": "def get_weather(location): ...",
    "status": "active",
    "description": "Get weather information for a location"
  }'
```

### 3. Associate Workflow with Agent
```bash
curl -X PUT "http://localhost:8000/agents/assistant" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_names": ["get_weather"]
  }'
```

### 4. Create a Chat
```bash
curl -X POST "http://localhost:8000/chats" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Chat",
    "agent_name": "assistant"
  }'
```

### 5. Send a Message
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "your-chat-id",
    "agent_name": "assistant",
    "message": "Hello! How can you help me?"
  }'
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_KEY` | API key for authentication | Yes |
| `MONGO_URI` | MongoDB connection string | Yes |
| `MONGO_DB_NAME` | MongoDB database name | Yes |
| `AZURE_GPT4O_BASE_URL` | Azure OpenAI endpoint | Yes |
| `AZURE_GPT4O_KEY` | Azure OpenAI API key | Yes |
| `AZURE_GPT4O_API_VERSION` | Azure OpenAI API version | Yes |

## 🎨 Key Features

### Dynamic Agent Building
Agents are built at runtime by:
1. Fetching agent configuration from MongoDB
2. Loading associated workflows
3. Building a complete system prompt that includes workflow descriptions
4. Creating an agent instance using AgentBuilder
5. Invoking the agent with chat history

### Workflow Integration
- Workflows are stored in MongoDB with their code and metadata
- When an agent is invoked, descriptions of its associated workflows are automatically added to the system prompt
- This allows the agent to understand what capabilities it has access to

### Persistent Chat History
- All messages are stored in MongoDB
- Full conversation context is maintained across sessions
- Messages include timestamps and role information

## 📁 Project Structure

```
backend/
├── app/
│   ├── database/
│   │   ├── mongo_db.py              # MongoDB connection
│   │   ├── schemas.py               # Pydantic models
│   │   ├── agent_queries.py         # Agent CRUD
│   │   ├── workflow_queries.py      # Workflow CRUD
│   │   └── new_chat_queries.py      # Chat CRUD
│   ├── routes/
│   │   ├── agents.py                # Agent endpoints
│   │   ├── workflows.py             # Workflow endpoints
│   │   ├── chats.py                 # Chat endpoints
│   │   └── chat_agent.py            # Main chat endpoint
│   ├── services/
│   │   └── agent_service.py         # Runtime agent builder
│   ├── utils/
│   │   ├── new_lifespan.py          # App lifecycle
│   │   └── logger.py                # Logging utilities
│   ├── config/
│   │   ├── env.py                   # Environment config
│   │   └── default.py               # Default configs
│   └── main_new.py                  # FastAPI app
├── requirements.txt
└── .env.example
```

## 🔒 Security Notes

- Always use environment variables for sensitive data
- Implement proper API key authentication
- Use HTTPS in production
- Configure CORS appropriately for your frontend domain
- Consider implementing rate limiting

## 🚧 Removed from Original

The refactored version removes:
- PostgreSQL database and SQLAlchemy
- Complex workflow deployment to Azure Functions
- Twilio voice integration
- Stripe payment webhooks
- Azure DevOps repository connectors
- Cognitive memory system (Azure AI Search)
- Business-specific logic (apartment booking, etc.)

These can be added back as optional modules/plugins later.

## 🎯 Next Steps

1. Add workflow execution engine
2. Implement tool/function calling for workflows
3. Add WebSocket support for real-time chat
4. Create frontend UI
5. Add user authentication and multi-tenancy
6. Implement workflow versioning
7. Add agent performance metrics

## 📝 License

[Your License Here]

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
