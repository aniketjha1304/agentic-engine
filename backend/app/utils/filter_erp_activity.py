import logging
from textwrap import dedent
from typing_extensions import TypedDict
from app.config.default import default_llm_dict


class FilterErpSignal(TypedDict):
    important_erp_signal: bool
    curated_erp_signal_message: str


async def filter_erp_activity(erp_message):
    """Analyze an ERP signal to determine its importance and summarize it if necessary."""

    logging.info("Filtering ERP signal message")
    logging.info(f"Received message: {erp_message}")

    prompt = dedent(
        f"""
        Analyze the following ERP signal message and determine if it is important.
        
        A signal is considered **important** if it involves actions related to:
        - Orders (e.g., new order placed, order canceled, order updated)
        - Master data (e.g., customer, product, or supplier updates)
        - Transactional data (e.g., invoice generated, payment processed)

        Signals related to **logins, general system events, or non-business operations** are NOT important.

        If the signal is important, summarize it concisely in a human-readable format.

        **ERP Signal Message to Analyze:**
        {erp_message}

        **Respond with a JSON object containing:**
        - `"important_erp_signal"`: `true` or `false`
        - `"curated_erp_signal_message"`: A summarized version of the message if important, otherwise an empty string.
        """
    )

    try:
        llm_response = (
            await default_llm_dict["azure_openai_gpt4o"]
            .with_structured_output(FilterErpSignal, strict=True)
            .ainvoke(prompt)
        )

        important_signal = llm_response.get("important_erp_signal", False)
        curated_message = llm_response.get("curated_erp_signal_message", "")
        curated_message = f"{curated_message}\n # Raw sigal from ERP:\n {erp_message}"

        logging.info(f"ERP Signal Importance: {important_signal}")
        logging.error(f"Curated Message: {curated_message}")

        return important_signal, curated_message

    except Exception as e:
        logging.error(f"Error processing ERP signal: {e}", exc_info=True)
        return False, ""  # Return defaults in case of failure
