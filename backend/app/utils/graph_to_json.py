def graph_to_json(graph):
    nodes = []
    for node_id, node in graph.nodes.items():
        nodes.append(
            {
                "id": node_id,
                "label": node.name,
                "type": getattr(
                    node.data, "__class__", {"__name__": "default"}
                ).__name__,
                "metadata": node.metadata or {},
            }
        )

    edges = []
    for edge in graph.edges:
        edges.append(
            {
                "source": edge.source,
                "target": edge.target,
                "label": "",  # Add label if necessary
                "conditional": edge.conditional,
            }
        )

    graph_json = {"nodes": nodes, "edges": edges}

    return graph_json
