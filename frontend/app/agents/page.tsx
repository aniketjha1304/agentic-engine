'use client';

import { useState } from 'react';
import useSWR from 'swr';
import Link from 'next/link';
import { toast } from 'sonner';
import { PlusIcon, TrashIcon } from '@/components/icons';
import { Button } from '@/components/ui/button';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { agentsAPI, type Agent } from '@/lib/api';
import { AgentForm } from '@/components/agent-form';

export default function AgentsPage() {
  const [deleteAgent, setDeleteAgent] = useState<Agent | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editAgent, setEditAgent] = useState<Agent | null>(null);

  const { data: agents = [], isLoading, mutate } = useSWR<Agent[]>(
    'agents',
    () => agentsAPI.getAll()
  );

  const handleDelete = async () => {
    if (!deleteAgent) return;

    try {
      await agentsAPI.delete(deleteAgent.name);
      toast.success(`Agent "${deleteAgent.name}" deleted successfully`);
      mutate();
      setDeleteAgent(null);
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete agent');
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="border-b px-6 py-4">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <div>
            <h1 className="text-2xl font-semibold">Agents</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Manage your AI agents and their configurations
            </p>
          </div>
          <div className="flex gap-2">
            <Link href="/">
              <Button variant="outline">Back to Chat</Button>
            </Link>
            <Button onClick={() => setCreateDialogOpen(true)}>
              <PlusIcon />
              Create Agent
            </Button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-6xl mx-auto">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-muted-foreground">Loading agents...</div>
            </div>
          ) : agents.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="text-4xl mb-4">🤖</div>
              <h2 className="text-xl font-semibold mb-2">No agents yet</h2>
              <p className="text-muted-foreground mb-6 max-w-md">
                Create your first agent to start building intelligent workflows and
                automations.
              </p>
              <Button onClick={() => setCreateDialogOpen(true)}>
                <PlusIcon />
                Create Your First Agent
              </Button>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {agents.map((agent) => (
                <div
                  key={agent.name}
                  className="border rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg">{agent.name}</h3>
                      <p className="text-xs text-muted-foreground mt-1">
                        Created {new Date(agent.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setDeleteAgent(agent)}
                      className="text-destructive hover:text-destructive"
                    >
                      <TrashIcon />
                    </Button>
                  </div>

                  <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                    {agent.system_prompt}
                  </p>

                  <div className="flex items-center justify-between">
                    <div className="text-xs text-muted-foreground">
                      {agent.workflow_names.length} workflow
                      {agent.workflow_names.length !== 1 ? 's' : ''}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setEditAgent(agent)}
                    >
                      Edit
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Create Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Agent</DialogTitle>
            <DialogDescription>
              Define your agent's behavior and assign workflows
            </DialogDescription>
          </DialogHeader>
          <AgentForm
            onSuccess={() => {
              setCreateDialogOpen(false);
              mutate();
            }}
            onCancel={() => setCreateDialogOpen(false)}
          />
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={!!editAgent} onOpenChange={(open: boolean) => !open && setEditAgent(null)}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Agent</DialogTitle>
            <DialogDescription>
              Update your agent's configuration
            </DialogDescription>
          </DialogHeader>
          {editAgent && (
            <AgentForm
              agent={editAgent}
              onSuccess={() => {
                setEditAgent(null);
                mutate();
              }}
              onCancel={() => setEditAgent(null)}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <AlertDialog open={!!deleteAgent} onOpenChange={(open) => !open && setDeleteAgent(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Agent</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{deleteAgent?.name}</strong>?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
