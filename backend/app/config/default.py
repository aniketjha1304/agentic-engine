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
