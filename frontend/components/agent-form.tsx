'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { agentsAPI, workflowsAPI, type Agent, type Workflow } from '@/lib/api';
import useSWR from 'swr';

interface AgentFormProps {
  agent?: Agent;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function AgentForm({ agent, onSuccess, onCancel }: AgentFormProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: agent?.name || '',
    system_prompt: agent?.system_prompt || '',
    workflow_names: agent?.workflow_names || [],
  });

  // Fetch available workflows
  const { data: workflows = [] } = useSWR<Workflow[]>(
    'workflows',
    () => workflowsAPI.getAll()
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (agent) {
        // Update existing agent
        await agentsAPI.update(agent.name, {
          system_prompt: formData.system_prompt,
          workflow_names: formData.workflow_names,
        });
        toast.success('Agent updated successfully');
      } else {
        // Create new agent
        await agentsAPI.create({
          name: formData.name,
          system_prompt: formData.system_prompt,
          workflow_names: formData.workflow_names,
        });
        toast.success('Agent created successfully');
      }

      onSuccess?.();
      router.refresh();
    } catch (error: any) {
      toast.error(error.message || 'Failed to save agent');
    } finally {
      setLoading(false);
    }
  };

  const toggleWorkflow = (workflowName: string) => {
    setFormData((prev) => ({
      ...prev,
      workflow_names: prev.workflow_names.includes(workflowName)
        ? prev.workflow_names.filter((w) => w !== workflowName)
        : [...prev.workflow_names, workflowName],
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="name">Agent Name *</Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="e.g., customer_support_agent"
          required
          disabled={!!agent || loading}
        />
        <p className="text-sm text-muted-foreground">
          Unique identifier for your agent (cannot be changed after creation)
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="system_prompt">System Prompt *</Label>
        <Textarea
          id="system_prompt"
          value={formData.system_prompt}
          onChange={(e) =>
            setFormData({ ...formData, system_prompt: e.target.value })
          }
          placeholder="You are a helpful AI assistant..."
          rows={6}
          required
          disabled={loading}
        />
        <p className="text-sm text-muted-foreground">
          Instructions that define your agent's behavior and personality
        </p>
      </div>

      <div className="space-y-2">
        <Label>Workflows (Optional)</Label>
        <div className="border rounded-md p-4 space-y-2 max-h-48 overflow-y-auto">
          {workflows.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No workflows available. Create workflows first to assign them to agents.
            </p>
          ) : (
            workflows.map((workflow) => (
              <label
                key={workflow.name}
                className="flex items-center space-x-2 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={formData.workflow_names.includes(workflow.name)}
                  onChange={() => toggleWorkflow(workflow.name)}
                  disabled={loading}
                  className="rounded"
                />
                <div>
                  <div className="text-sm font-medium">{workflow.name}</div>
                  {workflow.description && (
                    <div className="text-xs text-muted-foreground">
                      {workflow.description}
                    </div>
                  )}
                </div>
              </label>
            ))
          )}
        </div>
        <p className="text-sm text-muted-foreground">
          Select workflows this agent can execute
        </p>
      </div>

      <div className="flex gap-2 justify-end">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={loading}>
          {loading ? 'Saving...' : agent ? 'Update Agent' : 'Create Agent'}
        </Button>
      </div>
    </form>
  );
}
