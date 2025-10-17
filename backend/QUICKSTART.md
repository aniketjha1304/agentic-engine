# 🚀 Quick Start Guide - Agentic Engine

This guide will help you get the refactored Agentic Engine up and running in minutes.

## Prerequisites

- Python 3.8 or higher
- MongoDB (local or cloud instance like MongoDB Atlas)
- Azure OpenAI API access

## Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Setup MongoDB

### Option A: Local MongoDB with Docker
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Option B: MongoDB Atlas (Cloud)
1. Sign up at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get your connection string

## Step 3: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values
# At minimum, set:
# - API_KEY
# - MONGO_URI
# - AZURE_GPT4O_BASE_URL
# - AZURE_GPT4O_KEY
```

## Step 4: Run the Application

```bash
# Make sure you're in the backend directory
uvicorn app.main_new:app --reload --port 8000
```

## Step 5: Test the API

Open your browser to http://localhost:8000/docs to see the interactive API documentation.

## Example Workflow

### 1. Create Your First Agent

```bash
curl -X POST "http://localhost:8000/agents" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_assistant",
    "system_prompt": "You are a helpful AI assistant specialized in answering questions.",
    "workflow_names": []
  }'
```

### 2. Create a Chat Session

```bash
curl -X POST "http://localhost:8000/chats" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Chat",
    "agent_name": "my_assistant"
  }'
```

**Note the `id` returned - you'll need it for the next step!**

### 3. Send Your First Message

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "YOUR_CHAT_ID_HERE",
    "agent_name": "my_assistant",
    "message": "Hello! Can you help me understand what you can do?"
  }'
```

## Testing with the Web UI

Navigate to http://localhost:8000/docs and use the "Try it out" buttons to:
1. Create agents
2. Create workflows
3. Create chats
4. Send messages

## Common Issues

### MongoDB Connection Error
- **Issue**: Can't connect to MongoDB
- **Solution**: Ensure MongoDB is running and the MONGO_URI is correct

### Import Errors
- **Issue**: Module not found errors
- **Solution**: Ensure you've installed all requirements: `pip install -r requirements.txt`

### API Key Error
- **Issue**: Unauthorized errors
- **Solution**: Make sure you're sending the X-API-Key header with your requests

## Next Steps

1. **Create Workflows**: Define reusable skills for your agents
2. **Associate Workflows**: Link workflows to agents so they know what they can do
3. **Build Your Frontend**: Connect your UI to these APIs
4. **Customize Agents**: Experiment with different system prompts

## File Structure Overview

```
backend/
├── app/
│   ├── main_new.py           # Start here - main application
│   ├── routes/               # API endpoints
│   ├── services/             # Business logic
│   ├── database/             # MongoDB operations
│   └── config/               # Configuration
├── requirements.txt          # Dependencies
└── .env                      # Your configuration
```

## Development Tips

1. **Use the /docs endpoint** - It's your best friend for testing
2. **Check logs** - The application logs all operations
3. **Start simple** - Create one agent, one chat, test it
4. **Iterate** - Add workflows and complexity gradually

## Need Help?

- Check the logs for detailed error messages
- Review the API documentation at /docs
- Ensure all environment variables are set correctly
- Verify MongoDB is accessible

Happy building! 🎉
