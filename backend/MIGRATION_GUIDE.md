# 🔄 Migration Guide - Old to New Architecture

This guide helps you migrate from the PostgreSQL-based system to the new MongoDB-based architecture.

## Overview of Changes

| Aspect | Old System | New System |
|--------|-----------|------------|
| Database | PostgreSQL (2 databases) | MongoDB (1 database, 3 collections) |
| ORM | SQLAlchemy | Motor (async driver) |
| Agent Storage | Database + Files | MongoDB collection |
| Workflows | Azure DevOps + Functions | MongoDB collection |
| Main File | `app/main.py` | `app/main_new.py` |

## Step-by-Step Migration

### 1. Data Export from Old System

#### Export Agents (if applicable)
```python
# Run this against your old PostgreSQL database
import asyncpg

async def export_agents():
    conn = await asyncpg.connect('your_old_db_url')
    agents = await conn.fetch('''
        SELECT name, system_prompt, workflow_names
        FROM agents
    ''')
    # Save to JSON
    import json
    with open('agents_export.json', 'w') as f:
        json.dump([dict(r) for r in agents], f)
```

#### Export Workflows
```python
async def export_workflows():
    conn = await asyncpg.connect('your_old_db_url')
    workflows = await conn.fetch('''
        SELECT title as name, code, status, description
        FROM workflow
    ''')
    with open('workflows_export.json', 'w') as f:
        json.dump([dict(r) for r in workflows], f)
```

#### Export Chats
```python
async def export_chats():
    conn = await asyncpg.connect('your_old_db_url')
    
    # Export chats
    chats = await conn.fetch('SELECT * FROM chat')
    
    # Export messages
    for chat in chats:
        messages = await conn.fetch(
            'SELECT * FROM message WHERE chat_id = $1',
            chat['id']
        )
        # Process and save
```

### 2. Setup New System

```bash
# Install dependencies
pip install -r requirements.txt

# Setup MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### 3. Import Data to New System

Create an import script:

```python
# import_data.py
import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient

async def import_to_mongodb():
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["agentic_engine"]
    
    # Import Agents
    with open('agents_export.json') as f:
        agents = json.load(f)
        if agents:
            await db.agents.insert_many(agents)
            print(f"Imported {len(agents)} agents")
    
    # Import Workflows
    with open('workflows_export.json') as f:
        workflows = json.load(f)
        if workflows:
            await db.workflows.insert_many(workflows)
            print(f"Imported {len(workflows)} workflows")
    
    # Import Chats
    with open('chats_export.json') as f:
        chats = json.load(f)
        if chats:
            await db.chats.insert_many(chats)
            print(f"Imported {len(chats)} chats")

if __name__ == '__main__':
    asyncio.run(import_to_mongodb())
```

Run the import:
```bash
python import_data.py
```

### 4. Update API Calls

#### Old Agent Creation
```python
# Old way
POST /deploy_workflow
{
  "title": "My Workflow",
  "code": "...",
  "workflow_input_signature": {...}
}
```

#### New Agent Creation
```python
# New way
POST /agents
{
  "name": "my_agent",
  "system_prompt": "...",
  "workflow_names": []
}
```

#### Old Chat Invocation
```python
# Old way
POST /lisa-chat
{
  "chatId": "...",
  "messages": [...]
}
```

#### New Chat Invocation
```python
# New way
POST /chat
{
  "chat_id": "...",
  "agent_name": "my_agent",
  "message": "Hello"
}
```

### 5. Environment Variable Mapping

| Old Variable | New Variable | Notes |
|-------------|--------------|-------|
| `CHAT_DB_URL` | `MONGO_URI` | Changed to MongoDB |
| `AI_PERSONA_HUB_DB_URL` | `MONGO_URI` | Same URI, single DB |
| `ORGANIZATION_ID` | *(removed)* | Use agent names instead |
| All others | Same | Azure OpenAI configs unchanged |

### 6. Code Changes for Frontend/Clients

#### Update Endpoints
```javascript
// Old
const response = await fetch('/lisa-chat', {
  method: 'POST',
  body: JSON.stringify({
    chatId: id,
    messages: msgs
  })
});

// New
const response = await fetch('/chat', {
  method: 'POST',
  body: JSON.stringify({
    chat_id: id,
    agent_name: 'assistant',
    message: userMessage
  })
});
```

#### Update Response Handling
```javascript
// Old response structure
{
  message: [{role: "assistant", content: "..."}],
  workflow: {...}
}

// New response structure
{
  message: "...",
  chat_id: "..."
}
```

### 7. Workflow Migration Strategy

Old workflows in Azure Functions need to be:

1. **Extracted**: Get the code from Azure DevOps
2. **Stored**: Save in MongoDB workflows collection
3. **Described**: Add clear descriptions
4. **Associated**: Link to relevant agents

Example:
```python
# Old: Workflow in Azure Functions
# function_app.py
@app.route('/book-apartment')
def book_apartment(req):
    # ... code ...

# New: Workflow in MongoDB
POST /workflows
{
  "name": "book_apartment",
  "code": "def book_apartment(...): ...",
  "description": "Books an apartment for guests",
  "status": "active",
  "endpoint": "/execute/book_apartment"  # If you add execution later
}
```

### 8. Testing Checklist

- [ ] MongoDB is running and accessible
- [ ] All environment variables are set
- [ ] Dependencies are installed
- [ ] Data is imported successfully
- [ ] Health check passes: `GET /health`
- [ ] Can create an agent: `POST /agents`
- [ ] Can create a chat: `POST /chats`
- [ ] Can send a message: `POST /chat`
- [ ] Chat history is persisted
- [ ] Workflows are associated with agents

### 9. Run Both Systems in Parallel (Recommended)

During migration, run both systems:

```bash
# Terminal 1 - Old system
uvicorn app.main:app --port 8000

# Terminal 2 - New system  
uvicorn app.main_new:app --port 8001
```

Gradually migrate frontend calls from port 8000 → 8001

### 10. Common Migration Issues

#### Issue: MongoDB Connection Fails
**Solution**: Check MONGO_URI format
```bash
# Local
mongodb://localhost:27017

# Atlas
mongodb+srv://user:pass@cluster.mongodb.net/
```

#### Issue: Agent Not Found
**Solution**: Ensure agents are created with correct names
```python
# Agent names must match exactly
POST /agents with name="assistant"
POST /chat with agent_name="assistant"  # Must match!
```

#### Issue: Chat History Not Working
**Solution**: Verify chat_id is being stored and passed correctly
```python
# 1. Create chat, save the returned ID
response = POST /chats
chat_id = response.json()['id']

# 2. Use that exact ID in messages
POST /chat with chat_id=chat_id
```

## Rollback Plan

If you need to rollback:

1. Keep old system running
2. Switch frontend back to old endpoints
3. MongoDB data is preserved for retry

## Benefits After Migration

✅ Simpler infrastructure (one database)  
✅ Easier to understand and maintain  
✅ Better for open source contributions  
✅ More flexible agent configuration  
✅ Easier to add new features  

## Timeline Recommendation

- **Week 1**: Setup new system, import data
- **Week 2**: Run both systems in parallel
- **Week 3**: Migrate frontend API calls
- **Week 4**: Monitor and fix issues
- **Week 5**: Decommission old system

## Need Help?

1. Check logs for detailed errors
2. Verify MongoDB connection
3. Test endpoints individually with /docs
4. Compare old vs new data structures

---

**Remember**: Take backups before starting migration!
