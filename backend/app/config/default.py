from langchain_openai import AzureChatOpenAI, ChatOpenAI
from app.config.env import (
    AZURE_GPT4O_API_VERSION,
    AZURE_GPT4O_BASE_URL,
    AZURE_GPT4O_KEY,
)


# llm = ChatOpenAI(
#     model="gpt-4o",
#     api_key=os.getenv("OPENAI_KEY"),
#     base_url=os.getenv("OPENAI_BASE_URL"),
# )
llm = AzureChatOpenAI(
    base_url=AZURE_GPT4O_BASE_URL,
    api_key=AZURE_GPT4O_KEY,
    api_version=AZURE_GPT4O_API_VERSION,
    # streaming=True,
    # temperature=0.5,
)


default_llm_dict = {"azure_openai_gpt4o": llm}


# Default branch name for workflows
DEFAULT_WORKFLOW_BRANCH_NAME = "main"
DEFAULT_FUNCTION_BRANCH = "main"
DEFAULT_WORKFLOW_STATUS = "Inactive"
WORKFLOW_ACTIVE_STATUS = "Active"


# Workflow TYpes
WORKFLOW_TYPE_HTTP_TRIGGER = "http_trigger_workflow"
WORKFLOW_TYPE_SCHEDULED = "scheduled_workflow"


# Default values for workflow
DEFAULT_TOTAL_RUNS = 0
DEFAULT_TOTAL_COST = 0
DEFAULT_PRICE_PER_RUN = 1

# Adress for csg website guests page
CSG_GUESTS_WEBSITE_ADDRESS = (
    "https://www.siedlungsgemeinschaft.de/mieterservice/gaestewohnungen.html"
)
