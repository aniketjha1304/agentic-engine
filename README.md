# Agentic Engine

**A Dynamic Agent Orchestration Platform for Building Autonomous AI Systems**

Agentic Engine is an open-source platform that enables dynamic creation, management, and deployment of AI agents with reliable workflow orchestration. Build autonomous agents that can execute complex workflows, manage tasks, and adapt to any use case through intelligent runtime composition.

---

## Core Concepts

**Autonomous Agents** are intelligent systems that can reason, plan, and execute actions to accomplish goals. However, for production systems, pure autonomy without guardrails can be unreliable. **Workflows** provide structured, tested operations that agents can leverage.

**Agentic Engine bridges this gap** by combining:
- **Autonomous decision-making** through large language models
- **Reliable execution** through pre-defined, validated workflows
- **Dynamic composition** where agents are built at runtime based on configuration

This architecture is **use-case agnostic** - the same platform can power customer support, DevOps automation, data processing, or any domain-specific application.

---

## Architecture Overview

The platform consists of four key layers working in harmony:

**1. Management Layer**
- Web interface for creating and configuring agents
- Workflow library for defining reusable operations
- Chat interface for interacting with deployed agents

**2. Orchestration Layer**
- FastAPI backend exposing RESTful APIs
- Agent service that builds agents dynamically at runtime
- Workflow execution service with input validation
- Authentication and authorization

**3. Intelligence Layer**
- LangGraph for agent reasoning and planning
- Agent Builder for runtime composition
- Tool system for agent capabilities
- Azure OpenAI GPT-4 for language understanding

**4. Persistence Layer**
- MongoDB for flexible schema storage
- Collections for agents, workflows, and conversations
- Async operations for high performance

```
┌─────────────────────────────────────────────────────────────┐
│                    Management Layer                          │
│   [Agent Config] [Workflow Library] [Chat Interface]        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 Orchestration Layer                          │
│  [FastAPI] [Agent Service] [Workflow Service] [Auth]        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Intelligence Layer                          │
│    [LangGraph] [Agent Builder] [Tools] [GPT-4]              │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Persistence Layer                           │
│         [MongoDB: Agents | Workflows | Chats]               │
└─────────────────────────────────────────────────────────────┘
```

---

## The Novel Architecture

---

## The Novel Architecture

### Separation of Autonomy and Reliability

Traditional approaches fall into two camps:

**Pure Agentic Systems**: Fully autonomous agents that can take any action. Highly flexible but unpredictable and difficult to control in production.

**Pure Workflow Systems**: Rigid, deterministic workflows. Reliable and testable but inflexible and require explicit paths for every scenario.

**Agentic Engine combines both paradigms**:

```
Traditional Agentic System:
  User Request → Agent → Unpredictable Actions → Unknown Outcome
  
Traditional Workflow System:
  User Request → Fixed Path → Predefined Actions → Expected Outcome

Agentic Engine:
  User Request → Autonomous Agent → Discovers Workflows → Executes Reliably → Validated Outcome
```

The agent has **autonomy in deciding WHAT to do** while workflows provide **reliability in HOW it's done**.

### Dynamic Agent Composition

Agents are not statically coded but **composed at runtime**:

**Configuration Phase** (Stored in Database):
```
Agent Definition:
  - name: "customer_support"
  - system_prompt: "You are a helpful support agent..."
  - workflow_names: ["create_ticket", "send_email", "search_kb"]
  - llm_config: {temperature: 0.7, model: "gpt-4"}
```

**Runtime Composition** (Happens on Each Request):
```
1. Fetch agent configuration from MongoDB
2. Retrieve associated workflow definitions
3. Build enhanced system prompt with workflow descriptions
4. Attach workflow discovery and execution tools
5. Initialize LangGraph agent with Azure OpenAI
6. Return ready-to-use agent instance
```

This means:
- **No code changes** needed to create new agents
- **Instant updates** when workflows are modified
- **Context-aware agents** that know their capabilities
- **Separation of concerns** between agent logic and business operations

### Workflow as First-Class Citizens

Workflows are not mere functions but **managed entities** with:

**Identity**: Unique name, description, and status
**Contract**: JSON Schema defining input parameters
**Implementation**: Python code or HTTP endpoint
**Validation**: Automatic input validation before execution
**Discoverability**: Agents can query available workflows

This enables:
- **Reusability**: Same workflow across multiple agents
- **Testability**: Workflows validated independently
- **Composability**: Complex workflows built from simple ones
- **Governance**: Control what agents can and cannot do

### Intelligent Workflow Discovery

Agents don't hardcode workflow calls. Instead, they use three core tools:

**1. list_workflows()**: Discover available capabilities
**2. get_workflow_details(name)**: Understand workflow requirements
**3. execute_workflow(name, input_data)**: Execute with validation

Example interaction:
```
User: "Send a summary report to john@company.com"

Agent reasoning:
  1. Calls list_workflows() → Discovers "generate_report" and "send_email"
  2. Calls get_workflow_details("generate_report") → Learns required inputs
  3. Calls get_workflow_details("send_email") → Learns email parameters
  4. Executes generate_report({type: "summary"})
  5. Executes send_email({to: "john@company.com", subject: "Summary", body: report_data})

Result: Complex multi-step operation accomplished through intelligent orchestration
```

### Use-Case Agnostic Design

The same platform infrastructure supports radically different applications:

**Customer Support**: Agents with ticket creation, knowledge base search, escalation workflows
**DevOps Automation**: Agents with deployment, monitoring, incident response workflows  
**Data Processing**: Agents with ETL, validation, reporting workflows
**Content Management**: Agents with generation, editing, publishing workflows

The key insight: **domain logic lives in workflows, intelligence lives in agents**.

---

## Technology Stack

### Backend
- **FastAPI**: High-performance async Python web framework
- **MongoDB with Motor**: Async document database for flexible schemas
- **LangGraph**: Agent orchestration and reasoning framework
- **LangChain**: LLM integration and tool management
- **Azure OpenAI**: GPT-4 for natural language understanding
- **Pydantic**: Data validation and serialization

### Frontend  
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Shadcn/ui**: Accessible component library

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher with pnpm
- MongoDB (local or cloud instance)
- Azure OpenAI API key

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables - create `.env` file:
   ```env
   # MongoDB
   MONGODB_URL=mongodb://localhost:27017
   MONGODB_DB_NAME=agentic_engine

   # Azure OpenAI
   AZURE_OPENAI_API_KEY=your_azure_openai_key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
   AZURE_OPENAI_API_VERSION=2024-02-15-preview

   # API Security
   API_KEYS=your_secret_api_key_here
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main_new:app --host 0.0.0.0 --port 8000 --reload
   ```

   API available at `http://localhost:8000` with docs at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   pnpm install
   ```

3. Configure environment variables - create `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_API_KEY=your_secret_api_key_here
   ```

4. Start the development server:
   ```bash
   pnpm dev
   ```

   Application available at `http://localhost:3000`

---

## Key Features

**Dynamic Agent Management**: Create, configure, and deploy agents without code changes. Modify behavior by updating configuration.

**Workflow Library**: Build a library of reusable, tested workflows that agents can discover and execute.

**Runtime Composition**: Agents are built on-demand, ensuring they always have latest workflow information.

**Input Validation**: JSON Schema validation prevents invalid workflow execution.

**Conversation Memory**: Full chat history maintained for context-aware responses.

**Tool-based Architecture**: Agents use tools to discover and interact with workflows, enabling flexible orchestration.

---

## Use Cases

### Enterprise Automation
Deploy agents with workflows for document processing, approval routing, and notification systems.

### Customer Operations  
Create support agents with ticket management, email communication, and knowledge base workflows.

### Development Operations
Build DevOps agents with deployment, monitoring, rollback, and incident management workflows.

### Data Operations
Implement data agents with ETL, validation, transformation, and reporting workflows.

### Content Operations
Deploy content agents with generation, editing, approval, and publishing workflows.

The platform adapts to your domain by simply defining appropriate workflows.

---

## Project Structure

```
agentic-engine/
├── backend/
│   ├── app/
│   │   ├── config/              # Configuration and environment
│   │   ├── database/            # MongoDB schemas and queries
│   │   ├── routes/              # API endpoints
│   │   ├── services/            # Business logic layer
│   │   ├── tools/               # Agent tool implementations
│   │   ├── utils/               # Utilities and helpers
│   │   └── main_new.py          # FastAPI application
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/                     # Next.js pages
│   ├── components/              # React components
│   ├── lib/                     # API clients and utilities
│   ├── package.json
│   └── .env.local
│
└── README.md
```

---

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with clear commit messages
4. Push to your fork (`git push origin feature/amazing-feature`)
5. Open a Pull Request with a detailed description

Please ensure code follows existing style conventions and includes appropriate tests.

---

## Documentation

- **API Reference**: See `backend/API_DOCUMENTATION.md` for complete endpoint documentation
- **Architecture Details**: Review `backend/INTERACTIVE_COMPONENTS.md` for system design
- **Interactive Swagger**: Visit `http://localhost:8000/docs` when running locally

---

## Philosophy

Agentic Engine is built on key principles:

**Autonomy with Guardrails**: Agents make decisions, workflows ensure reliability
**Configuration over Code**: Deploy new capabilities without development cycles  
**Use-Case Agnostic**: One platform serves unlimited domains
**Runtime Composition**: Agents built fresh with latest context
**Separation of Concerns**: Intelligence layer separate from business logic

---

## Roadmap

- Multi-agent collaboration and task delegation
- Workflow marketplace for sharing and discovery
- Vector database integration for RAG capabilities
- Real-time WebSocket support for live updates
- Multi-LLM support (OpenAI, Anthropic, local models)
- Advanced analytics and observability
- Kubernetes deployment configurations
- Plugin system for extensibility

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

Built with [LangChain](https://langchain.com), [LangGraph](https://langchain.com/langgraph), [FastAPI](https://fastapi.tiangolo.com), [Next.js](https://nextjs.org), and [MongoDB](https://www.mongodb.com).

---

<div align="center">

**Agentic Engine** - Autonomous Intelligence, Reliable Execution

[Documentation](backend/API_DOCUMENTATION.md) · [Issues](https://github.com/aniketjha1304/agentic-engine/issues) · [Discussions](https://github.com/aniketjha1304/agentic-engine/discussions)

</div>