import type { SetStateAction } from 'react';
import { Button } from './ui/button';
import { WorkflowIcon } from './icons'; // You'll need to create or import an appropriate icon
import { WorkflowBlockProps }  from './workflow-block';


// Define the Workflow interface
export interface Workflow {
  id: string;
  title: string;
  description: string;
  content: string; // Code content
  diagram: Diagram; // Adjusted to match the new response
  status: string;
  metadata: Record<string, any>;
}

export interface Diagram {
  nodes: DiagramNode[];
  edges: DiagramEdge[];
}

export interface DiagramNode {
  id: string;
  label: string;
  type?: string;
  metadata?: Record<string, any>;
}

export interface DiagramEdge {
  source: string;
  target: string;
  label?: string;
  conditional?: boolean;
}

  interface WorkflowResultProps {
    workflow: Workflow;
    setBlock: (value: SetStateAction<WorkflowBlockProps>) => void;
  }
  
  export function WorkflowResult({ workflow, setBlock }: WorkflowResultProps) {
    return (
      <Button
        variant="outline"
        className="bg-background cursor-pointer border py-2 px-3 rounded-xl w-fit flex flex-row gap-3 items-start"
        onClick={(event) => {
          const rect = event.currentTarget.getBoundingClientRect();
  
          const boundingBox = {
            top: rect.top,
            left: rect.left,
            width: rect.width,
            height: rect.height,
          };
  
          setBlock({
            workflow,
            isVisible: true,
            boundingBox,
          });
        }}
      >
        <div className="text-muted-foreground mt-1">
          <WorkflowIcon />
        </div>
        <div className="text-left">
          {`Workflow "${workflow.title}"`}
        </div>
      </Button>
    );
  }