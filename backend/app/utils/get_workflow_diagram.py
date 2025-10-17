import logging
from app.utils.run_code import run_code
from app.utils.graph_to_json import graph_to_json


# Get a logger for this module
logger = logging.getLogger(__name__)


def get_workflow_diagram(workflow_code: str):
    # Run the code to get the workflow graph
    workflow_diagram = None
    data = run_code(workflow_code)
    workflow_graph = data.get("workflow_graph")

    if workflow_graph is not None:

        # Convert the graph to JSON
        try:
            workflow_diagram = graph_to_json(workflow_graph.get_graph(xray=True))
        except:
            workflow_diagram = graph_to_json(workflow_graph.get_graph(xray=False))
    return workflow_diagram
