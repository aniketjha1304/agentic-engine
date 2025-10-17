[![python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

| Environment | Version |
| ----------- | ------- |
| Production  | 0.0.1   |
| Development | 0.0.1   |

# Lisa Engine

**Lisa Engine** is an application designed to expose **Lisa**, an AI persona built to assist with material planning and task management within client organizations. The application leverages  [LangGraph](https://langchain-ai.github.io/langgraph/) and is served using a Flask endpoint.

## About Lisa

**Lisa** is an AI persona built on top of LangGraph, implementing a multi-agent architecture. She serves as a material planner for client organizations, offering intelligent assistance in task execution, management and workflow automation.

## Features and Capabilities

### 1. Ad-hoc Task Management

- **Task Creation**: Create to-do lists and manage tasks.
- **Communication**: Send emails, check inbox messages, and access data on SharePoint.
- **Data Access**: Interact with data repositories (Sharepoint) and other resources.

### 2. Workflow Learning and Execution

- **Delegation**: Users can delegate workflows to Lisa for her to learn.
- **Learning Ability**: Learns sequences of logical tasks needed to accomplish specific jobs or objectives.
- **Intelligent Execution**: Executes learned workflows intelligently and monitors it.

### 3. Proactive Action and Intelligence

- **Autonomous Actions**: Initiates appropriate workflows or actions without explicit prompts based on her intelligence.

## Folder Structure

The project follows a modular structure for easier management and scalability.
```
LISA-ENGINE/
├── app/                     # Main application code
│   ├── config/              # Configuration files (e.g., default values, prompts for agents)
│   ├── controllers/         # Controllers to handle business logic of API
│   ├── utils/               # Utility scripts and helpers
│   ├── routes/              # Flask route definitions (To be added)
│   ├── main.py              # Main file for FastAPI application.
│   └── graph/               # Graphs and Sub-graphs definition
│        ├── nodes/          # Graph logic folder
│        ├── graph_state.py  # State of the graph.
│        └── lisa_graph.py   # Realization of Lisa Graph.
├── venv/                    # Python virtual environment (ignored if you're using a virtualenv)
├── .env                     # Environment variables for the project
├── .env.development         # Environment variables for the development environment
├── .gitignore               # Git ignore file to avoid committing unnecessary files
├── Dockerfile               # Docker configuration to containerize the app
├── logo.png                 # Project logo (used in README or other documentation)
├── README.md                # Project README file with instructions
└── requirements.txt         # Python dependencies for the project
```
## Environment Variables

| **Variable Name**               | **Description**                                                       |
|----------------------------------|-----------------------------------------------------------------------|
| `AZURE_GPT4O_KEY`                | API key for authenticating with Azure GPT-4 OpenAI service            |
| `AZURE_GPT4O_BASE_URL`           | Base URL for the Azure GPT-4 OpenAI API                               |
| `AZURE_GPT4O_API_VERSION`       | API version for Azure GPT-4 OpenAI service                            |
| `LANGCHAIN_TRACING_V2`          | Enable LangChain tracing (`true` or `false`)                          |
| `LANGCHAIN_ENDPOINT`            | Endpoint for the LangChain API                                        |
| `LANGCHAIN_API_KEY`             | API key for LangChain services                                        |
| `LANGCHAIN_PROJECT`             | Project name identifier for LangChain                                 |
| `CLIENT_ID`                     | Client ID for authenticating with Azure services                      |
| `LISA_USER_NAME`                | Username for Lisa's account                                           |
| `LISA_PASSWORD`                 | Password for Lisa's account                                           |
| `AZURE_PAT_TOKEN`               | Personal Access Token (PAT) for Azure authentication                  |
| `CHAT_DB_DATABASE_URL`          | Connection URL for the Chat database                                  |
| `API_KEY`                       | API Key for Lisa Engine authentication                                |
| `WORKFLOW_FUNCTION_APP_URL`     | Azure Functions app URL for workflow execution                        |
| `WORKFLOW_FUNCTION_APP_MASTER_KEY` | API key for functions app authentication                           |
| `DEVOPS_ORGANIZATION_NAME`             | Azure DevOps organization name                                        |
| `PROJECT_NAME`                  | Azure DevOps project name                                             |
| `WORKFLOWS_REPO_NAME`           | Azure DevOps repository name for workflows                            |
| `WORKFLOW_FUNCTIONS_REPO_NAME`  | Azure DevOps repository name for workflow functions                   |
| `ORGANIZATION_ID`               | Organization ID for Azure DevOps                                      |


## How to Run Locally

To run the Lisa Engine service on your local machine, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://RecallSpace@dev.azure.com/RecallSpace/recall-space-developments/_git/lisa-engine
    ```

2. Navigate to the project directory:

    ```bash
    cd lisa-engine
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```
4. Install the memory package and agent_builder package.
    There are two ways to install the packages.
    1) Installing from artifacts
    2) Installing from local repository or git in editable non editable mode.
    To install from local in editable mode navigate to the recall-space-agents package repository on local and run the following command
    ```bash
    pip install -e .
    ```
5. Start the FastAPI server using Uvicorn:

    ```bash
    uvicorn app.main:app --reload     
    ```
---

## Deploying on container app
- For deploying you need to create a docker image on your local with latest changes and push to registry
```bash
az login
az acr login --name recallcontainers.azurecr.io
docker build --build-arg PAT=<your-pat-token> -t lisa-engine .
docker tag lisa-engine:provisional recallcontainers.azurecr.io/lisa-engine:provisional
docker push recallcontainers.azurecr.io/lisa-engine:provisional
```
- Once pushed the changes to registry, restart the container.

## Deploying on container app (dev)
- For deploying you need to create a docker image on your local with latest changes and push to registry
```bash
az login
az acr login --name recallcontainers.azurecr.io
docker build --build-arg PAT=<your-pat-token> -t lisa-engine-dev .
docker tag lisa-engine-dev:latest recallcontainers.azurecr.io/lisa-engine-dev:latest
docker push recallcontainers.azurecr.io/lisa-engine-dev:latest
```
- Once pushed the changes to registry, restart the container.
# Lisa's Architecture

Lisa is built with a multi-agent architecture to meet its desired capabilities. The system is structured around two primary node types: **Assistant Nodes** and **Tool Nodes**.

---

## Architecture Overview


:::mermaid
graph TD
    __start__([<p>__start__</p>]):::first
    gating_assistant(gating_assistant)
    gating_assistant_tools(gating_assistant_tools)
    task_executor_assistant(task_executor_assistant)
    task_executor_tools(task_executor_tools)
    workflow_configurer_assistant(workflow_configurer_assistant)
    workflow_configurer_tools(workflow_configurer_tools)
    __end__([<p>__end__</p>]):::last
    
    __start__ --> gating_assistant
    gating_assistant_tools --> gating_assistant
    task_executor_tools --> task_executor_assistant
    workflow_configurer_tools --> workflow_configurer_assistant
    gating_assistant -.-> gating_assistant_tools
    gating_assistant -.-> task_executor_assistant
    gating_assistant -.-> workflow_configurer_assistant
    gating_assistant -.-> __end__
    task_executor_assistant -.-> task_executor_tools
    task_executor_assistant -.-> gating_assistant
    workflow_configurer_assistant -.-> workflow_configurer_tools
    workflow_configurer_assistant -.-> gating_assistant
:::
This architecture enables Lisa to dynamically handle tasks, manage workflows, and effectively communicate between its components while maintaining a modular and scalable design.

### Node Types:
1. **Assistant Nodes**:
   - AI agents with tools which do tasks autonomously.
   - Each Assistant Node has its own message channel for communication.
   - Can interact with:
     - Other Assistant Nodes by sending human-like messages to their channels and receiving tool messages in response.
     - Their corresponding Tool Nodes for specific operations.

2. **Tool Nodes**:
   - Contain a set of tools for specialized operations.
   - Tools can:
     - Update the state of graph (Only via Command).
     - Return a response, which is converted into a tool message.

---

## Components and Their Roles

### **Gating Node**:
- **Assistant Node**: `gating_assistant`
  - Acts as the primary interface for Lisa.
  - Routes requests to appropriate Assistant Nodes or utilizes its Tool Node.
  - Capabilities:
    - Handle general questions.
    - Facilitate routing between nodes.
- **Tool Node**: `gating_assistant_tools`
  - Tools:
    - `GetWorkflows`
    - `ExecuteWorkflows`
    - `FetchLatestWorkflowRun`
- **Message Channel**: `messages`
---

### **Workflow Management Node**:
- **Assistant Node**: `workflow_configurer_assistant`
  - Manages the creation and updating of workflows.
- **Tool Node**: `workflow_configurer_tools`
  - Tools:
    - `SaveWorkflow`
    - `GenerateWorkflowCode`
- **Message Channel**: `workflow_configurer_messages`
---

### **Task Execution Node**:
- **Assistant Node**: `task_executor_assistant`
  - Executes ad-hoc tasks like sending emails.
- **Tool Node**: `task_executor_tools`
  - Tools:
    - `aget_emails`
    - `asend_email`
    - `aextract_text_from_file_by_path`
    - `asearch_and_extract_text`
    - `alist_files_and_folders_in_path`
    - `alist_worksheets_in_workbook`
    - `alist_tables_in_worksheet`
    - `aget_table_content`
    - `aget_table_row_by_index`
    - `alist_files_and_folders_in_path`
    - `aapply_filter_to_table`
    - `aupdate_cells_values`
    - `aadd_row_to_table`
    - `acreate_todo_list`
    - `adelete_todo_list`
    - `acreate_task`
    - `adelete_task`
    - `acomplete_task`
    - `alist_tasks_due_today`
    - `alist_tasks_in_todo_list`
  - **Message Channel**: `task_executor_messages`
---

## Communication Flow
1. Messages from the Front-End (FE) application are routed to the `gating_assistant`.
2. The `gating_assistant` determines whether to:
   - Route the request to another Assistant Node.
   - Use a tool from its own Tool Node.
3. Each Assistant Node communicates via its own message channel:
   - When the `gating_assistant` interacts with another Assistant Node, it sends a human-like message to that node's channel.
   - The responding node processes the message, performs actions, and returns a tool message to the `gating_assistant`.

## Communication Between Agents
Below is an example of communication between agents in our multi-agent architecture of Lisa.

:::mermaid
sequenceDiagram
    participant User as User
    participant Gating as gating_assistant
    participant Configurer as workflow_configurer_assistant
    participant Tools as workflow_configurer_tools

    User->>Gating: Request (e.g., "Generate workflow ...")
    Gating->>Gating: Determine next step using `determine_next_action`  
    Gating->>Gating: Process response using `transfer_to_assistant`  
    Gating->>Gating: Push response on `messages` channel  
    Gating->>Configurer: Forward request on `workflow_configurer_messages` channel (as human message)
    
    Configurer->>Configurer: Process request  
    Configurer->>Tools: Call `GenerateWorkflowCode`  
    Tools-->>Configurer: Return response (Generated code)  
    Configurer->>Tools: Call `SaveWorkflow`  
    Tools-->>Configurer: Return response (Workflow saved)  
    
    Configurer->>Configurer: Update its own `workflow_configurer_messages` channel  
    Configurer-->>Gating: Send `ToolMessage` (Final response) on `messages` channel for Gating assistant  
    
    Gating->>User: Return final response to User

:::
---

## Workflow State Management
- The `workflow` state is central to Lisa's operation.
- Created and updated by the `workflow_configurer_assistant` via its tool (`SaveWorkflow`).
- If a `workflow` exists, the FE renders it as a component.

---
+ Each execution of Lisa could be traced on langsmith under the run name `Lisa AI` with  `Lisa` tag.
+ The prompts for WorkflowCodeGenerator and WorkflowConfigurer are fetched from `workflows` repository `/prompts/`
### Notes on `Deploy Workflow`

:::mermaid
sequenceDiagram
    participant User
    participant AI-Persona-Hub (Next.js App)
    participant Lisa Engine
    participant Workflow Azure Function Repo
    participant Workflow CD Pipeline
    participant Workflow Function App (Azure)

    User->>AI-Persona-Hub (Next.js App): Send request to deploy workflow
    AI-Persona-Hub (Next.js App)->>Lisa Engine: Forward request to deploy-workflow endpoint
    activate Lisa Engine
    Lisa Engine->>Lisa Engine: Use WorkflowAzureFunctionBuilder to generate Azure function
    Lisa Engine->>Workflow Azure Function Repo: Build and publish function code to 'main' branch
    Lisa Engine-->>AI-Persona-Hub (Next.js App): Return response with message and route
    deactivate Lisa Engine
    AI-Persona-Hub (Next.js App)->>AI-Persona-Hub (Next.js App): Update workflow table and add route
    Workflow Azure Function Repo->>Workflow CD Pipeline: Trigger pipeline
    Workflow CD Pipeline->>Workflow Function App (Azure): Deploy functions to Azure
:::
## WorkflowAzureFunctionBuilder: Overview and Key Concepts

The `WorkflowAzureFunctionBuilder` class is designed to automate the process of generating and deploying Azure Functions based on workflow metadata. Here's a brief overview and key concepts:

### Purpose
- **Automation**: Facilitates the creation of Azure Functions for workflows using metadata and code from a repository.
- **Deployment**: Pushes the generated function code and workflow code to an Azure DevOps repository and triggers the CI/CD pipeline.

### Key Components
1. **Initialization**: 
   - Accepts either a `workflow_id` or `title` to identify the workflow.
   - Establishes a connection to the functions repository via the `AzureRepoConnector` utility.

2. **Process Workflow**:
   - Fetches workflow metadata and code.
   - Generates Azure Function code based on the workflow type (HTTP or Timer trigger).
   - Pushes the code to the functions repository and adds required `__init__.py` files for Python packaging.

3. **Trigger Types**:
   - **HTTP Trigger**: Creates a function with a specific route URL for HTTP requests.
   - **Timer Trigger**: Creates a scheduled function with a cron-like schedule.

---

### Naming and Directory Structure

#### Workflow Title Management
- The **workflow title** is used to generate a unique folder name using the `generate_folder_name` utility.
- Workflow code file names are derived from the folder name and stored as `<folder_name>.py`.

#### Directory Structure
- Based on the trigger type:
  - **HTTP Trigger Workflows**: Stored in `workflows/http_trigger/<folder_name>`.
  - **Scheduled Workflows**: Stored in `workflows/scheduled/<folder_name>`.
  
- Each folder contains:
  - `function_app.py`: The Azure Function definition.
  - `<folder_name>.py`: The workflow code file.
  - `__init__.py`: Empty files in each directory to ensure Python packaging compatibility.

#### Example
For a workflow titled "Daily Report Generator":
- **Folder Name**: `daily_report_generator`
- **Directory Structure**: `
markdown
Copy code
## WorkflowAzureFunctionBuilder: Overview and Key Concepts

The `WorkflowAzureFunctionBuilder` class is designed to automate the process of generating and deploying Azure Functions based on workflow metadata. Here's a brief overview and key concepts:

### Purpose
- **Automation**: Facilitates the creation of Azure Functions for workflows using metadata and code from a repository.
- **Deployment**: Pushes the generated function code and workflow code to an Azure DevOps repository and triggers the CI/CD pipeline.

### Key Components
1. **Initialization**: 
   - Accepts either a `workflow_id` or `title` to identify the workflow.
   - Establishes a connection to the functions repository via the `AzureRepoConnector` utility.

2. **Process Workflow**:
   - Fetches workflow metadata and code.
   - Generates Azure Function code based on the workflow type (HTTP or Timer trigger).
   - Pushes the code to the functions repository and adds required `__init__.py` files for Python packaging.

3. **Trigger Types**:
   - **HTTP Trigger**: Creates a function with a specific route URL for HTTP requests.
   - **Timer Trigger**: Creates a scheduled function with a cron-like schedule.

---

### Naming and Directory Structure

#### Workflow Title Management
- The **workflow title** is used to generate a unique folder name using the `generate_folder_name` utility.
- Workflow code file names are derived from the folder name and stored as `<folder_name>.py`.

#### Directory Structure
- Based on the trigger type:
  - **HTTP Trigger Workflows**: Stored in `workflows/http_trigger/<folder_name>`.
  - **Scheduled Workflows**: Stored in `workflows/scheduled/<folder_name>`.
  
- Each folder contains:
  - `function_app.py`: The Azure Function definition.
  - `<folder_name>.py`: The workflow code file.
  - `__init__.py`: Empty files in each directory to ensure Python packaging compatibility.

#### Example
For a workflow titled "Daily Report Generator":
- **Folder Name**: `daily_report_generator`
- **Directory Structure**:
```
├── workflows/                # Root directory for workflow Azure Functions
│   ├── http_trigger/         # Directory for HTTP-triggered workflows
│   │   ├── daily_report_generator/  # Workflow-specific folder
│   │   │   ├── function_app.py      # Azure Function definition
│   │   │   ├── daily_report_generator.py  # Workflow code file
│   │   │   ├── __init__.py          # Empty file for Python packaging
│   ├── scheduled/            # Directory for scheduled workflows
```
### Route URL
- For HTTP triggers, the `route` is derived from the metadata or defaults to the folder name.
- The route URL is constructed using the environment variable `WORKFLOW_FUNCTION_APP_URL` as the base.

### Error Handling
- Raises appropriate exceptions for missing metadata, code, or environment variables during the process.

This class simplifies the Azure Function deployment process by integrating metadata handling, code generation, and repository updates into a seamless workflow.
### Architectural notes
- The current method of handoff is via tool call and then we modify the state and messages
- Handoffs consists of two things: a) Destination b ) Payload
- Graph design is another topic, how to define agent nodes and what are states for them ?