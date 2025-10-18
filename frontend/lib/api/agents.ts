import { apiFetch } from './config';

// Agent Types
export interface Agent {
  name: string;
  system_prompt: string;
  workflow_names: string[];
  llm_config: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CreateAgentRequest {
  name: string;
  system_prompt: string;
  workflow_names?: string[];
  llm_config?: Record<string, any>;
}

export interface UpdateAgentRequest {
  system_prompt?: string;
  workflow_names?: string[];
  llm_config?: Record<string, any>;
}

export interface AgentWithWorkflows {
  agent: Agent;
  workflows: any[];
}

// Agent API Functions
export const agentsAPI = {
  // Get all agents
  getAll: async (): Promise<Agent[]> => {
    return apiFetch<Agent[]>('/agents');
  },

  // Get agent by name
  getByName: async (name: string): Promise<AgentWithWorkflows> => {
    return apiFetch<AgentWithWorkflows>(`/agents/${name}`);
  },

  // Create agent
  create: async (data: CreateAgentRequest): Promise<Agent> => {
    return apiFetch<Agent>('/agents', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Update agent
  update: async (name: string, data: UpdateAgentRequest): Promise<Agent> => {
    return apiFetch<Agent>(`/agents/${name}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  // Delete agent
  delete: async (name: string): Promise<void> => {
    return apiFetch<void>(`/agents/${name}`, {
      method: 'DELETE',
    });
  },
};
