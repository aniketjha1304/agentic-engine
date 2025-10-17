import uuid
from datetime import datetime, timezone
from sqlalchemy import text
from app.database.db_connect import get_ai_persona_hub_db, get_chat_db
from app.config.env import ORGANIZATION_ID
from app.config.default import (
    WORKFLOW_TYPE_HTTP_TRIGGER,
    WORKFLOW_TYPE_SCHEDULED,
    DEFAULT_TOTAL_RUNS,
    DEFAULT_TOTAL_COST,
    DEFAULT_PRICE_PER_RUN,
    WORKFLOW_ACTIVE_STATUS
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def get_workflow_by_title(title: str):

    query = text(
        """
        SELECT * FROM workflow
        WHERE title = :title AND organization_id = :organization_id
        LIMIT 1
        """
    )

    async with get_ai_persona_hub_db() as db:
        result = await db.execute(
            query, {"title": title, "organization_id": ORGANIZATION_ID}
        )
        # Fetch the first row matching the query
        row = result.fetchone()

        if row:
            row_dict = dict(zip(result.keys(), row))
            return row_dict
    return None


async def get_http_trigger_workflow_data(workflow_id: str):

    query = text(
        """
        SELECT * FROM http_trigger_workflow
        WHERE workflow_id = :workflow_id 
        LIMIT 1
        """
    )

    async with get_ai_persona_hub_db() as db:
        result = await db.execute(
            query, {"workflow_id": workflow_id, "organization_id": ORGANIZATION_ID}
        )
        # Fetch the first row matching the query
        row = result.fetchone()

        if row:
            # Convert the row to a dictionary
            return dict(zip(result.keys(), row))

    return None


async def get_scheduled_workflow_data(workflow_id: str):

    query = text(
        """
        SELECT * FROM scheduled_workflow
        WHERE workflow_id = :workflow_id 
        LIMIT 1
        """
    )

    async with get_ai_persona_hub_db() as db:
        result = await db.execute(
            query, {"workflow_id": workflow_id, "organization_id": ORGANIZATION_ID}
        )
        # Fetch the first row matching the query
        row = result.fetchone()

        if row:
            # Convert the row to a dictionary
            return dict(zip(result.keys(), row))

    return None


async def update_workflow_run(workflow_title: str, number_of_runs: int):
    """
    Update the total_runs and total_cost for the specified workflow based on the given number_of_runs.

    Args:
        workflow_title (str): The title of the workflow to update.
        number_of_runs (int): The number of runs to add to total_runs.
        organization_id (int): The ID of the organization.

    Returns:
        None
    """
    organization_id = ORGANIZATION_ID
    query_fetch = text(
        """
        SELECT id, total_runs, price_per_run FROM workflow
        WHERE title = :workflow_title AND organization_id = :organization_id
        LIMIT 1
        """
    )

    query_fetch_budget = text(
        """
        SELECT budget FROM payment
        WHERE organization_id = :organization_id
        LIMIT 1
        """
    )

    query_update_workflow_run = text(
        """
        UPDATE workflow
        SET total_runs = :total_runs,
            total_cost = :total_cost
        WHERE id = :workflow_id AND organization_id = :organization_id
        """
    )
    query_update_budget = text(
        """
        UPDATE payment
        SET budget = :updated_budget 
        WHERE organization_id = :organization_id
        """
    )

    async with get_ai_persona_hub_db() as db:
        async with db.begin():  # Begin a transaction
            # Fetch workflow data
            result = await db.execute(
                query_fetch,
                {"workflow_title": workflow_title, "organization_id": organization_id},
            )
            row = result.fetchone()
            if not row:
                raise ValueError(f"Workflow with title '{workflow_title}' not found.")
            row = dict(zip(result.keys(), row))

            # Fetch payment budget
            result_budget = await db.execute(
                query_fetch_budget,
                {"organization_id": organization_id},
            )
            row_budget = result_budget.fetchone()
            if not row_budget:
                raise ValueError("Subscription budget not found.")
            row_budget = dict(zip(result_budget.keys(), row_budget))

            # Extract data and calculate new values
            workflow_id = row["id"]
            current_total_runs = row["total_runs"]
            price_per_run = row["price_per_run"]
            budget = row_budget["budget"]

            new_total_runs = current_total_runs + number_of_runs
            new_total_cost = new_total_runs * price_per_run
            updated_budget = budget - number_of_runs * price_per_run

            # Update workflow and budget
            await db.execute(
                query_update_workflow_run,
                {
                    "total_runs": new_total_runs,
                    "total_cost": new_total_cost,
                    "workflow_id": workflow_id,
                    "organization_id": organization_id,
                },
            )
            await db.execute(
                query_update_budget,
                {
                    "updated_budget": updated_budget,
                    "organization_id": organization_id,
                },
            )
            await db.commit()


async def is_budget_sufficient(workflow_title: str, number_of_runs: int):
    """
    Checks if the organization's budget is sufficient to execute the specified number of workflow runs.

    Args:
        workflow_title (str): The title of the workflow.
        number_of_runs (int): The number of runs to be executed.

    Returns:
        bool: True if the budget is sufficient, False otherwise.
    """
    organization_id = ORGANIZATION_ID

    query_fetch_price = text(
        """
        SELECT price_per_run FROM workflow
        WHERE title = :workflow_title AND organization_id = :organization_id
        LIMIT 1
        """
    )

    query_fetch_budget = text(
        """
        SELECT budget FROM payment
        WHERE organization_id = :organization_id
        LIMIT 1
        """
    )

    async with get_ai_persona_hub_db() as db:
        async with db.begin():
            # Fetch price per run for the workflow
            result_price = await db.execute(
                query_fetch_price,
                {"workflow_title": workflow_title, "organization_id": organization_id},
            )
            row_price = result_price.fetchone()
            if not row_price:
                raise ValueError(f"Workflow with title '{workflow_title}' not found.")
            row_price = dict(zip(result_price.keys(), row_price))
            price_per_run = row_price["price_per_run"]

            # Fetch current budget
            result_budget = await db.execute(
                query_fetch_budget, {"organization_id": organization_id}
            )
            row_budget = result_budget.fetchone()
            if not row_budget:
                raise ValueError("Subscription budget not found.")
            row_budget = dict(zip(result_budget.keys(), row_budget))
            budget = row_budget["budget"]

            # Calculate required budget
            required_budget = number_of_runs * price_per_run

            # Check if budget is sufficient
            return budget >= required_budget and budget >= 0


async def get_workflows_list():
    query = text(
        f""" SELECT a.title, a.status, a.description, b.workflow_input_state  FROM
        (SELECT id, title, status, description, type, total_runs, created_at, updated_at
        FROM workflow
        WHERE organization_id = :organization_id
        AND status = '{WORKFLOW_ACTIVE_STATUS}') a
        LEFT JOIN 
        (SELECT workflow_id, workflow_input_state FROM http_trigger_workflow) b
        on a.id = b.workflow_id
        """
    )

    async with get_ai_persona_hub_db() as session:
        result = await session.execute(query, {"organization_id": ORGANIZATION_ID})
        rows = result.fetchall()

        if rows:
            output_rows = []
            for row in rows:
                row_dict = dict(zip(result.keys(), row))
                output_rows.append(row_dict)
            return output_rows
    return []

async def save_workflow(workflow_data: dict):
    """
    Save a new workflow record, including HTTP trigger and scheduled workflow.

    :param workflow_data: Dictionary containing workflow details.
    :return: Dict indicating success or failure
    """
    workflow_data["created_at"] = datetime.now()
    workflow_data["updated_at"] = datetime.now()

    base_query_insert = text(
        """
        INSERT INTO workflow (id, title, type, status, description, source_code_location,
                              total_runs, total_cost, price_per_run, organization_id,
                              accountable_user_id, created_at, updated_at)
        VALUES (:id, :title, :type, :status, :description, :source_code_location,
                :total_runs, :total_cost, :price_per_run, :organization_id,
                :accountable_user_id, :created_at, :updated_at)
        """
    )

    async with get_ai_persona_hub_db() as db:
        try:
            await db.execute(
                base_query_insert,
                {
                    "id": workflow_data["id"],
                    "title": workflow_data["title"],
                    "type": workflow_data["type"],
                    "status": workflow_data["status"],
                    "description": workflow_data["description"],
                    "source_code_location": workflow_data["source_code_location"],
                    "total_runs": DEFAULT_TOTAL_RUNS,
                    "total_cost": DEFAULT_TOTAL_COST,
                    "price_per_run": DEFAULT_PRICE_PER_RUN,
                    "organization_id": ORGANIZATION_ID,
                    "accountable_user_id": workflow_data["accountable_user_id"],
                    "created_at": workflow_data["created_at"],
                    "updated_at": workflow_data["updated_at"],
                },
            )

            await db.commit()

            # Handle specific workflow types
            if workflow_data["type"] == WORKFLOW_TYPE_HTTP_TRIGGER:
                await save_http_trigger_workflow(db, workflow_data["id"], workflow_data)
            elif workflow_data["type"] == WORKFLOW_TYPE_SCHEDULED:
                await save_scheduled_workflow(db, workflow_data["id"], workflow_data)

            return {"success": True, "message": "Workflow saved successfully."}
        except Exception as e:
            return {"success": False, "message": str(e)}


async def update_workflow(workflow_id: str, workflow_data: dict):
    """
    Update an existing workflow record, including HTTP trigger and scheduled workflow.

    :param workflow_data: Dictionary containing workflow details.
    :return: Dict indicating success or failure
    """
    workflow_data["updated_at"] = datetime.now()

    base_query_update = text(
        """
        UPDATE workflow
        SET title = :title,
            type = :type,
            status = :status,
            description = :description,
            source_code_location = :source_code_location,
            accountable_user_id = :accountable_user_id,
            updated_at = :updated_at
        WHERE id = :id AND organization_id = :organization_id
        """
    )

    async with get_ai_persona_hub_db() as db:
        try:
            await db.execute(
                base_query_update,
                {
                    "id": workflow_id,
                    "title": workflow_data["title"],
                    "type": workflow_data["type"],
                    "status": workflow_data["status"],
                    "description": workflow_data["description"],
                    "source_code_location": workflow_data["source_code_location"],
                    "accountable_user_id": workflow_data["accountable_user_id"],
                    "updated_at": workflow_data["updated_at"],
                    "organization_id": ORGANIZATION_ID,
                },
            )

            await db.commit()

            # Handle specific workflow types
            if workflow_data["type"] == WORKFLOW_TYPE_HTTP_TRIGGER:
                await update_http_trigger_workflow(
                    db, workflow_data["id"], workflow_data
                )
            elif workflow_data["type"] == WORKFLOW_TYPE_SCHEDULED:
                await update_scheduled_workflow(db, workflow_data["id"], workflow_data)

            return {"success": True, "message": "Workflow updated successfully."}
        except Exception as e:
            return {"success": False, "message": str(e)}


async def save_http_trigger_workflow(db, workflow_id: int, workflow_data: dict):
    query = text(
        """
        INSERT INTO http_trigger_workflow ( workflow_id, workflow_endpoint, workflow_input_state)
        VALUES ( :workflow_id, :workflow_endpoint, :workflow_input_state) 
        """
    )

    await db.execute(
        query,
        {
            # "id": str(uuid.uuid4()),
            "workflow_id": workflow_id,
            "workflow_endpoint": workflow_data.get("workflow_endpoint", ""),
            "workflow_input_state": workflow_data.get("workflow_input_state"),
        },
    )

    await db.commit()
    return {"success": True, "message": "HTTP trigger workflow saved successfully."}


async def update_workflow_status(workflow_title: str, workflow_status: str):

    base_query_update = text(
        """
        UPDATE workflow
        SET status = :workflow_status  
        WHERE title = :workflow_title AND organization_id = :organization_id
        """
    )

    async with get_ai_persona_hub_db() as db:
        try:
            await db.execute(
                base_query_update,
                {
                    "organization_id": ORGANIZATION_ID,
                    "workflow_title": workflow_title,
                    "workflow_status": workflow_status,
                },
            )

            await db.commit()

            return {"success": True, "message": "Workflow status updated successfully."}
        except Exception as e:
            return {"success": False, "message": str(e)}


async def set_http_workflow_endpoint(workflow_id: int, workflow_endpoint: str):

    query = text(
        """
        UPDATE http_trigger_workflow
        SET workflow_endpoint = :workflow_endpoint 
        WHERE workflow_id = :workflow_id
        """
    )

    async with get_ai_persona_hub_db() as db:
        try:
            await db.execute(
                query,
                {
                    "workflow_id": workflow_id,
                    "workflow_endpoint": workflow_endpoint,
                },
            )

            await db.commit()

            return {"success": True, "message": "Workflow endpoint set successfully."}
        except Exception as e:
            return {"success": False, "message": str(e)}


async def update_http_trigger_workflow(db, workflow_id: int, workflow_data: dict):
    query = text(
        """
        UPDATE http_trigger_workflow
        SET workflow_endpoint = :workflow_endpoint,
            workflow_input_state = :workflow_input_state
        WHERE workflow_id = :workflow_id
        """
    )

    await db.execute(
        query,
        {
            "workflow_id": workflow_id,
            "workflow_endpoint": workflow_data.get("workflow_endpoint"),
            "workflow_input_state": workflow_data.get("workflow_input_state"),
        },
    )

    await db.commit()
    return {
        "success": True,
        "message": "HTTP trigger workflow updated successfully.",
    }


async def save_scheduled_workflow(db, workflow_id: int, workflow_data: dict):
    query = text(
        """
        INSERT INTO scheduled_workflow ( workflow_id, cron_expression)
        VALUES ( :workflow_id, :cron_expression)
        """
    )

    await db.execute(
        query,
        {
            # "id": str(uuid.uuid4()),
            "workflow_id": workflow_id,
            "cron_expression": workflow_data.get("cron_expression"),
        },
    )

    await db.commit()
    return {"success": True, "message": "Scheduled workflow saved successfully."}


async def update_scheduled_workflow(db, workflow_id: int, workflow_data: dict):
    query = text(
        """
        UPDATE scheduled_workflow
        SET cron_expression = :cron_expression
        WHERE workflow_id = :workflow_id
        """
    )

    await db.execute(
        query,
        {
            "workflow_id": workflow_id,
            "cron_expression": workflow_data.get("cron_expression"),
        },
    )

    await db.commit()
    return {"success": True, "message": "Scheduled workflow updated successfully."}


async def delete_workflow_by_title(title: str):
    """
    Delete a workflow by title, ensuring related entries in workflows_to_tags, 
    http_trigger_workflow, and scheduled_workflow are deleted first.

    :param title: Title of the workflow to delete.
    :return: Dict indicating success or failure.
    """

    async with get_ai_persona_hub_db() as session:
        try:
            async with session.begin():  # Use a transaction
                # Delete related records in workflows_to_tags
                await session.execute(
                    text("""
                        DELETE FROM workflows_to_tags 
                        WHERE workflow_id IN (
                            SELECT id FROM workflow 
                            WHERE title = :title AND organization_id = :organization_id
                        )
                    """),
                    {"organization_id": ORGANIZATION_ID, "title": title}
                )
                # Now delete the workflow itself
                result = await session.execute(
                    text("""
                        DELETE FROM workflow
                        WHERE title = :title AND organization_id = :organization_id
                    """),
                    {"organization_id": ORGANIZATION_ID, "title": title}
                )

                await session.commit()
                logger.info("Workflow '%s' and its associated data deleted successfully.", title)
                return {"success": True, "message": f"Workflow '{title}' deleted."}

        except Exception as e:
            await session.rollback()  # Rollback in case of error
            logger.error("Error deleting workflow '%s': %s", title, str(e))
            return {"success": False, "message": f"Error deleting workflow '{title}': {str(e)}"}



async def delete_http_trigger_workflow(workflow_id: str):
    query = text(
        """
        DELETE FROM http_trigger_workflow
        WHERE workflow_id = :workflow_id
        """
    )
    async with get_ai_persona_hub_db() as db:
        await db.execute(query, {"workflow_id": workflow_id})
        await db.commit()
        return {
            "success": True,
            "message": "Http trigger workflow deleted successfully.",
        }


async def delete_scheduled_workflow(workflow_id: str):
    query = text(
        """
        DELETE FROM scheduled_workflow
        WHERE workflow_id = :workflow_id
        """
    )
    async with get_ai_persona_hub_db() as db:
        await db.execute(query, {"workflow_id": workflow_id})
        await db.commit()
        return {"success": True, "message": "Scheduled workflow deleted successfully."}


async def update_workflow_title_and_source_code_location(
    workflow_id: str, workflow_data: dict
):
    """
    Update an existing workflow record with new title and source code location

    :param workflow_data: Dictionary containing workflow details.
    :return: Dict indicating success or failure
    """
    workflow_data["updated_at"] = datetime.now()

    base_query_update = text(
        """
        UPDATE workflow
        SET title = :title,
            status = :status,
            source_code_location = :source_code_location,
            updated_at = :updated_at
        WHERE id = :id AND organization_id = :organization_id
        """
    )

    async with get_ai_persona_hub_db() as db:
        try:
            await db.execute(
                base_query_update,
                {
                    "id": workflow_id,
                    "title": workflow_data["title"],
                    "status": workflow_data["status"],
                    "source_code_location": workflow_data["source_code_location"],
                    "updated_at": workflow_data["updated_at"],
                    "organization_id": ORGANIZATION_ID,
                },
            )

            await db.commit()

            return {"success": True, "message": "Workflow updated successfully."}
        except Exception as e:
            return {"success": False, "message": str(e)}
