[![python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

| Environment | Version |
| ----------- | ------- |
| Production  | 0.0.1   |
| Development | 0.0.1   |

# Lisa Engine

**Lisa Engine** is an application designed to expose **Lisa**, an AI persona built to assist with material planning and task management within client organizations. The application leverages  [LangGraph](https://langchain-ai.github.io/langgraph/) and is served using a Flask endpoint.

## About Lisa

**Lisa** is an AI that serves as a material planner for client organizations, offering intelligent assistance in task execution, management and workflow automation.

## Cognitive Architeture Facts (04/15/2025)

+ Lisa's system prompt is composed by 3 elements
    1. General instructions, provision at run time from repository *Workflows* on prompts/lisa_chat_prompt.md
    2. Pull from the database with workflow/skills, names and parameters.
    3. Summary of the Memories on the index e.g. the latest `Core` memory.

### Index based brain
Lisa's brain has 4 types of memories `Semantic`, `episodic`, `Procedural` and `Core`, with the following structure.

```json
{
    "@search.score": 1,
    "id": "ed6bf0df477587d9a69ed30323bc00794d60ee86c165730c2be8c563727c5617",
    "content": "There will a new tariff on roadbikes like our FERT-SPEED being effective from April 30th onwards of 25% on the sales price. This will lower the demand by 50% past this date.",
    "optimized_text_search_content": "there will a new tariff on roadbik like our fertspe be effect from april 30th onward of 25 on the sale price thi will lower the demand by 50 past thi date",
    "timestamp": "2025-04-10T16:47:06.647Z",
    "metadata": "Facts",
    "type": "Semantic"
}
```

+ Memories of type `Core` are not meant to be used directly, they are sorted memories in the index, with the most recent one inserted on the prompt of Lisa.
+ Lisa learn new memories via skill execution "Knowledge Management" using the "AiSearchManager" worker agent. At the end of this workflow, the method `await ms_ai_search_tool_kit.summarize_recent_memories(llm=llm)` is called, so that new summary is created of the last 100 memories. Here we use `MapReduce`, more information [here](https://python.langchain.com/docs/versions/migrating_chains/map_reduce_chain/)
+ You can ask Lisa, the following to filter the semantic or text base search:
```
Lisa please use your memory_text_search(or memory_vector_search) with content search_text="*", top_n=10, type_filter="Procedural"
```
+ That will the latest 10 memories of type "Procedural"
+ memory_text_search and memory_vector_search do not include by default memories of type `Core`. To get those type of memories you would need to set it manually on the request:
```
Lisa please use your memory_text_search(or memory_vector_search) with content search_text="*", top_n=10, type_filter="Core"
```
