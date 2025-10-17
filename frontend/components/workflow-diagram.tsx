// WorkflowDiagram.tsx
import React, { useEffect } from 'react';
import ReactFlow, {
  Controls,
  Edge as FlowEdge,
  Node as FlowNode,
  useNodesState,
  useEdgesState,
  MarkerType,
  Position,
  NodeProps,
  Handle,
} from 'reactflow';
import 'reactflow/dist/style.css';
import * as dagre from '@dagrejs/dagre';

const blueColor = '#4F46E5'; // Tailwind's text-indigo-600 color

// Move the CustomNode component outside if it's not already
const CustomNode: React.FC<NodeProps> = ({ data }) => {
  const nodeStyle = {
    padding: 10,
    border: `3px solid ${blueColor}`, // Always thick blue border
    borderRadius: 10,
    backgroundColor: '#ffffff',
    color: '#000000', // Text color is black
    fontSize: '1.875rem', // Tailwind's text-3xl
    fontWeight: 600, // Tailwind's font-semibold
    textAlign: 'center' as const,
    width: '100%',
    height: '100%',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  };

  return (
    <div style={nodeStyle}>
      {data.label}
      <Handle type="target" position={Position.Top} />
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
};

// Define nodeTypes outside of the component
const nodeTypes = {
  custom: CustomNode,
};

interface DiagramNode {
  id: string;
  label: string;
  type?: string;
  metadata?: Record<string, any>;
}

interface DiagramEdge {
  source: string;
  target: string;
  label?: string;
  conditional?: boolean;
}

interface WorkflowDiagramProps {
  nodes: DiagramNode[];
  edges: DiagramEdge[];
}

export const WorkflowDiagram: React.FC<WorkflowDiagramProps> = ({ nodes, edges }) => {
  const nodeWidth = 200;
  const nodeHeight = 70;

  const getLayoutedElements = (nodes: FlowNode[], edges: FlowEdge[]) => {
    // Set up dagre graph
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));
    dagreGraph.setGraph({ rankdir: 'TB' }); // Top to Bottom layout

    // Add nodes
    nodes.forEach((node) => {
      dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
    });

    // Add edges
    edges.forEach((edge) => {
      dagreGraph.setEdge(edge.source, edge.target);
    });

    // Compute layout
    dagre.layout(dagreGraph);

    // Assign positions to nodes
    nodes.forEach((node) => {
      const nodeWithPosition = dagreGraph.node(node.id);
      node.position = {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      };
      node.targetPosition = Position.Top;
      node.sourcePosition = Position.Bottom;
    });

    return { nodes, edges };
  };

  // Initialize nodes and edges state
  const [rfNodes, setRfNodes, onNodesChange] = useNodesState<FlowNode>([]);
  const [rfEdges, setRfEdges, onEdgesChange] = useEdgesState<FlowEdge>([]);

  useEffect(() => {
    // Map your nodes to React Flow nodes
    const initialNodes: FlowNode[] = nodes.map((node) => ({
      id: node.id,
      data: { label: node.label },
      position: { x: 0, y: 0 },
      type: 'custom', // Use custom node
      width: nodeWidth,
      height: nodeHeight,
    }));

    // Map your edges to React Flow edges
    const initialEdges: FlowEdge[] = edges.map((edge, index) => ({
      id: `edge-${index}`,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      animated: edge.conditional,
      markerEnd: {
        type: edge.conditional ? MarkerType.ArrowClosed : MarkerType.Arrow,
        color: blueColor, // Arrowhead color remains blue
      },
      style: {
        stroke: blueColor, // Edge color remains blue
        strokeWidth: 3, // Increased edge thickness
      },
      labelStyle: { fill: blueColor }, // Label color remains blue
    }));

    const layoutedElements = getLayoutedElements(initialNodes, initialEdges);

    setRfNodes([...layoutedElements.nodes]);
    setRfEdges([...layoutedElements.edges]);
  }, [nodes, edges]);

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={rfNodes}
        edges={rfEdges}
        nodeTypes={nodeTypes} // nodeTypes is now defined outside
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Controls />
        {/* Background component removed to eliminate dots */}
      </ReactFlow>
    </div>
  );
};