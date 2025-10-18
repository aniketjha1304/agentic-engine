'use client';

import { startTransition, useMemo, useOptimistic, useState, useEffect } from 'react';
import useSWR from 'swr';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';
import { CheckCirclFillIcon, ChevronDownIcon } from './icons';
import { agentsAPI, type Agent } from '@/lib/api';

export function AgentSelector({
  selectedAgentName,
  onSelectAgent,
  className,
}: {
  selectedAgentName?: string;
  onSelectAgent?: (agentName: string) => void;
} & React.ComponentProps<typeof Button>) {
  const [open, setOpen] = useState(false);
  const [optimisticAgentName, setOptimisticAgentName] = useOptimistic(selectedAgentName || '');

  const { data: agents = [], isLoading } = useSWR<Agent[]>(
    'agents',
    () => agentsAPI.getAll()
  );

  const selectedAgent = useMemo(
    () => agents.find((agent) => agent.name === optimisticAgentName),
    [optimisticAgentName, agents]
  );

  // Auto-select first agent if none selected
  useEffect(() => {
    if (!selectedAgentName && agents.length > 0 && onSelectAgent) {
      onSelectAgent(agents[0].name);
    }
  }, [agents, selectedAgentName, onSelectAgent]);

  if (isLoading) {
    return (
      <Button variant="outline" className={cn('md:px-2 md:h-[34px]', className)} disabled>
        Loading...
      </Button>
    );
  }

  if (agents.length === 0) {
    return (
      <Button variant="outline" className={cn('md:px-2 md:h-[34px]', className)} disabled>
        No Agents
      </Button>
    );
  }

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger
        asChild
        className={cn(
          'w-fit data-[state=open]:bg-accent data-[state=open]:text-accent-foreground',
          className,
        )}
      >
        <Button variant="outline" className="md:px-2 md:h-[34px]">
          {selectedAgent?.name || 'Select Agent'}
          <ChevronDownIcon />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="min-w-[300px]">
        {agents.map((agent) => (
          <DropdownMenuItem
            key={agent.name}
            onSelect={() => {
              setOpen(false);
              startTransition(() => {
                setOptimisticAgentName(agent.name);
                onSelectAgent?.(agent.name);
              });
            }}
            className="gap-4 group/item flex flex-row justify-between items-center"
            data-active={agent.name === optimisticAgentName}
          >
            <div className="flex flex-col gap-1 items-start">
              <div className="font-medium">{agent.name}</div>
              <div className="text-xs text-muted-foreground line-clamp-1">
                {agent.system_prompt}
              </div>
            </div>
            <div className="text-primary dark:text-primary-foreground opacity-0 group-data-[active=true]/item:opacity-100">
              <CheckCirclFillIcon />
            </div>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
