'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { WorkflowIcon } from '@/components/icons';
import type { Workflow } from '@/lib/api/chats';

interface WorkflowCardProps {
  workflow: Workflow;
  onViewDetails: (workflow: Workflow) => void;
}

export function WorkflowCard({ workflow, onViewDetails }: WorkflowCardProps) {
  return (
    <Card 
      className="p-4 hover:bg-accent/50 transition-colors cursor-pointer group"
      onClick={() => onViewDetails(workflow)}
    >
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-primary/10 text-primary">
          <WorkflowIcon size={20} />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-sm mb-1 group-hover:text-primary transition-colors">
            {workflow.name}
          </h4>
          <p className="text-sm text-muted-foreground line-clamp-2">
            {workflow.description || 'No description available'}
          </p>
          {workflow.status && (
            <div className="mt-2">
              <span className={`text-xs px-2 py-0.5 rounded-full ${
                workflow.status === 'active' 
                  ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300' 
                  : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
              }`}>
                {workflow.status}
              </span>
            </div>
          )}
        </div>
        <Button 
          variant="ghost" 
          size="sm"
          className="opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={(e) => {
            e.stopPropagation();
            onViewDetails(workflow);
          }}
        >
          View Code
        </Button>
      </div>
    </Card>
  );
}
