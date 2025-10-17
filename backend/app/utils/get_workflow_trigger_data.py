from app.database.ai_persona_hub_queries import (
    get_http_trigger_workflow_data,
    get_scheduled_workflow_data,
)
from app.config.default import (
    WORKFLOW_TYPE_HTTP_TRIGGER,
)


async def get_workflow_trigger_data(workflow_id: str, trigger_type: str):

    if trigger_type == WORKFLOW_TYPE_HTTP_TRIGGER:
        # TODO: Add the query to get this data
        workflow_trigger_data = await get_http_trigger_workflow_data(
            workflow_id=workflow_id
        )
    else:
        workflow_trigger_data = await get_scheduled_workflow_data(
            workflow_id=workflow_id
        )
    print("Worflow Trigger Data: ", workflow_trigger_data)
    return workflow_trigger_data
