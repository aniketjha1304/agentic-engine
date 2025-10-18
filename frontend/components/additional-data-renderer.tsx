'use client';

import { useState } from 'react';
import { WorkflowCard } from '@/components/workflow-card';
import { WorkflowDetail } from '@/components/workflow-detail';
import type { AdditionalData, Workflow } from '@/lib/api/chats';

interface AdditionalDataRendererProps {
  data: AdditionalData;
}

export function AdditionalDataRenderer({ data }: AdditionalDataRendererProps) {
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);

  // Render workflows list
  if (data.workflows && data.workflows.length > 0) {
    return (
      <>
        <div className="mt-4 space-y-2">
          <div className="text-sm font-medium text-muted-foreground mb-3">
            Available Workflows ({data.workflows.length})
          </div>
          <div className="grid gap-2">
            {data.workflows.map((workflow, index) => (
              <WorkflowCard
                key={workflow.name || index}
                workflow={workflow}
                onViewDetails={setSelectedWorkflow}
              />
            ))}
          </div>
        </div>
        {selectedWorkflow && (
          <WorkflowDetail
            workflow={selectedWorkflow}
            onClose={() => setSelectedWorkflow(null)}
          />
        )}
      </>
    );
  }

  // Render single workflow detail
  if (data.workflow) {
    return (
      <>
        <div className="mt-4">
          <div className="text-sm font-medium text-muted-foreground mb-3">
            Workflow Details
          </div>
          <WorkflowCard
            workflow={data.workflow}
            onViewDetails={setSelectedWorkflow}
          />
        </div>
        {selectedWorkflow && (
          <WorkflowDetail
            workflow={selectedWorkflow}
            onClose={() => setSelectedWorkflow(null)}
          />
        )}
      </>
    );
  }

  // Future: Add more renderers for other data types
  // if (data.charts) return <ChartRenderer charts={data.charts} />
  // if (data.tables) return <TableRenderer tables={data.tables} />
  
  return null;
}
