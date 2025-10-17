# 🏗️ Architecture Diagrams

Visual representation of the new Agentic Engine architecture.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Web UI, Mobile App, API Clients, Third-party Integrations)    │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS/REST
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                     FastAPI Application                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   API Routes Layer                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │  │
│  │  │ Agents   │ │Workflows │ │  Chats   │ │   Chat   │   │  │
│  │  │   API    │ │   API    │ │   API    │ │  Agent   │   │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │  │
│  └───────┼────────────┼────────────┼────────────┼──────────┘  │
│          │            │            │            │              │
│  ┌───────▼────────────▼────────────▼────────────▼──────────┐  │
│  │              Services Layer                              │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │         Agent Service                            │    │  │
│  │  │  • Build agents at runtime                       │    │  │
│  │  │  • Compose system prompts                        │    │  │
│  │  │  • Integrate workflow descriptions               │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  └──────────────────────────┬───────────────────────────────┘  │
│                             │                                   │
│  ┌──────────────────────────▼───────────────────────────────┐  │
│  │              Database Layer                              │  │
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐ │  │
│  │  │ Agent Queries │  │Workflow Queries│  │Chat Queries │ │  │
│  │  └───────┬───────┘  └───────┬───────┘  └──────┬──────┘ │  │
│  └──────────┼──────────────────┼──────────────────┼─────────┘  │
└─────────────┼──────────────────┼──────────────────┼────────────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │       MongoDB            │
                    │  ┌──────────────────┐   │
                    │  │ agents           │   │
                    │  │ workflows        │   │
                    │  │ chats            │   │
                    │  └──────────────────┘   │
                    └──────────────────────────┘
```

## Request Flow Diagram

### Agent Creation Flow
```
┌──────────┐
│  Client  │
└────┬─────┘
     │ POST /agents
     │ {name, system_prompt, workflow_names}
     │
┌────▼─────────────┐
│  Agents Router   │
└────┬─────────────┘
     │
┌────▼──────────────┐
│ Agent Queries     │
│ • Validate data   │
│ • Check duplicates│
│ • Insert to DB    │
└────┬──────────────┘
     │
┌────▼──────────┐
│   MongoDB     │
│ agents coll.  │
└───────────────┘
```

### Chat Message Flow
```
┌──────────┐
│  Client  │
└────┬─────┘
     │ POST /chat
     │ {chat_id, agent_name, message}
     │
┌────▼──────────────────┐
│  Chat Agent Router    │
└────┬──────────────────┘
     │
     │ 1. Fetch chat history
┌────▼─────────────┐
│  Chat Queries    │────┐
└──────────────────┘    │
                        │
     │ 2. Add user message
     │                  │
┌────▼─────────────┐    │
│  Chat Queries    │    │
└──────────────────┘    │
                        │
     │ 3. Build agent   │
┌────▼──────────────┐   │
│  Agent Service    │   │
│  ┌─────────────┐  │   │
│  │ Fetch agent │◄─┼───┤
│  │ config      │  │   │
│  ├─────────────┤  │   │
│  │ Fetch       │◄─┼───┤
│  │ workflows   │  │   │
│  ├─────────────┤  │   │
│  │ Build prompt│  │   │
│  ├─────────────┤  │   │
│  │ Create agent│  │   │
│  └─────────────┘  │   │
└───────┬───────────┘   │
        │               │
     │ 4. Invoke agent  │
┌────▼─────────────┐    │
│  AgentBuilder    │    │
│  • LangChain     │    │
│  • Azure OpenAI  │    │
└────┬─────────────┘    │
     │                  │
     │ 5. Save response │
┌────▼─────────────┐    │
│  Chat Queries    │◄───┘
└────┬─────────────┘
     │
┌────▼──────────┐
│   MongoDB     │
│ chats coll.   │
└───────────────┘
     │
┌────▼─────┐
│  Client  │
└──────────┘
```

## Data Model Diagram

```
┌─────────────────────────────────┐
│          Agent                  │
├─────────────────────────────────┤
│ • name (unique)                 │
│ • system_prompt                 │
│ • workflow_names []             │◄────────┐
│ • llm_config {}                 │         │
│ • created_at                    │         │
│ • updated_at                    │         │
└─────────────────────────────────┘         │
                                            │
                                   references
                                            │
┌─────────────────────────────────┐         │
│        Workflow                 │         │
├─────────────────────────────────┤         │
│ • name (unique)                 │◄────────┘
│ • code                          │
│ • status                        │
│ • endpoint                      │
│ • attributes {}                 │
│ • description                   │
│ • created_at                    │
│ • updated_at                    │
└─────────────────────────────────┘


┌─────────────────────────────────┐
│           Chat                  │
├─────────────────────────────────┤
│ • id (uuid)                     │
│ • name                          │
│ • agent_name                    │─┐
│ • created_at                    │ │
│ • updated_at                    │ │
│ • messages []                   │ │
│   ├─ role                       │ │
│   ├─ content                    │ │
│   └─ timestamp                  │ │
└─────────────────────────────────┘ │
                                    │
                         references │
                                    │
┌─────────────────────────────────┐ │
│          Agent                  │ │
│  (from above)                   │◄┘
└─────────────────────────────────┘
```

## Agent Runtime Building

```
User Message Arrives
        │
        ▼
┌────────────────────┐
│ Fetch Agent Config │
│  from MongoDB      │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Fetch Workflows    │
│  by Names          │
└────────┬───────────┘
         │
         ▼
┌────────────────────────────────┐
│ Build Complete System Prompt   │
│                                 │
│  Base Prompt:                   │
│  "You are a helpful assistant"  │
│                                 │
│  + Workflow Descriptions:       │
│  "## Available Workflows        │
│   - get_weather: Get weather    │
│   - book_apt: Book apartment"   │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────┐
│ Create Agent       │
│  via AgentBuilder  │
│                    │
│ • Set LLM          │
│ • Set Prompt       │
│ • Add Tools        │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Invoke with        │
│ Message + History  │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Return Response    │
└────────────────────┘
```

## Deployment Architecture

### Development
```
┌────────────┐
│ Developer  │
│  Machine   │
│            │
│ MongoDB    │
│ (Docker)   │
│            │
│ FastAPI    │
│ (local)    │
└────────────┘
```

### Production (Recommended)
```
┌─────────────────────────────────────────┐
│            Load Balancer                │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────┐
│  FastAPI    │  │  FastAPI    │
│  Instance 1 │  │  Instance 2 │
└──────┬──────┘  └──────┬──────┘
       │                │
       └────────┬────────┘
                │
       ┌────────▼────────┐
       │   MongoDB       │
       │   (Atlas or     │
       │    Replica Set) │
       └─────────────────┘

┌─────────────────────────────┐
│    External Services        │
│  • Azure OpenAI             │
│  • Monitoring/Logging       │
└─────────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────┐
│         Application Layer           │
│  • FastAPI (Web Framework)          │
│  • Pydantic (Data Validation)       │
│  • Python 3.8+                      │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│        AI/Agent Layer               │
│  • agent-builder (Agent Framework)  │
│  • LangChain (Orchestration)        │
│  • Azure OpenAI (LLM)               │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│        Database Layer               │
│  • Motor (Async MongoDB Driver)     │
│  • MongoDB 5.0+                     │
└─────────────────────────────────────┘
```

## Security Architecture

```
┌──────────────┐
│   Client     │
└──────┬───────┘
       │ HTTPS
       │ X-API-Key Header
       │
┌──────▼───────────────┐
│  API Gateway/LB      │
│  • SSL Termination   │
│  • Rate Limiting     │
└──────┬───────────────┘
       │
┌──────▼───────────────┐
│  FastAPI             │
│  • API Key Verify    │
│  • CORS Config       │
│  • Input Validation  │
└──────┬───────────────┘
       │
┌──────▼───────────────┐
│  MongoDB             │
│  • Auth Enabled      │
│  • TLS Connection    │
│  • Role-based Access │
└──────────────────────┘
```

## Scalability Considerations

### Horizontal Scaling
```
Add more FastAPI instances
           │
           ▼
    Load Balancer
           │
     ┌─────┼─────┐
     ▼     ▼     ▼
   App1  App2  App3
     └─────┼─────┘
           ▼
    MongoDB Cluster
```

### Vertical Scaling
```
Increase resources per instance
• More CPU cores
• More RAM
• Better network
```

### Caching Layer (Future)
```
Client → FastAPI → Redis → MongoDB
                     ↑
                  Cache frequently
                  accessed data
```

---

## Notes

- **Stateless API**: Each FastAPI instance is stateless
- **Shared Database**: All instances connect to same MongoDB
- **Agent Building**: Done per-request (could be cached in future)
- **Message History**: Stored in MongoDB, retrieved per chat
- **Workflow Descriptions**: Dynamically added to prompts

