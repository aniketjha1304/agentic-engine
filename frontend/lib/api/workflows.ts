import { apiFetch } from './config';

// Workflow Types
export interface Workflow {
  name: string;
  code: string;
  status: string;
  endpoint: string;
  attributes: Record<string, any>;
  description: string;
  input_parameters: {
    type: string;
    properties: Record<string, any>;
    required?: string[];
  };
  created_at: string;
  updated_at: string;
}

export interface CreateWorkflowRequest {
  name: string;
  code: string;
  status?: string;
  endpoint?: string;
  attributes?: Record<string, any>;
  description?: string;
  input_parameters?: {
    type: string;
    properties: Record<string, any>;
    required?: string[];
  };
}

export interface UpdateWorkflowRequest {
  code?: string;
  status?: string;
  endpoint?: string;
  attributes?: Record<string, any>;
  description?: string;
  input_parameters?: {
    type: string;
    properties: Record<string, any>;
    required?: string[];
  };
}

export interface ExecuteWorkflowRequest {
  workflow_name: string;
  input_data: Record<string, any>;
}

export interface ExecuteWorkflowResponse {
  status: string;
  workflow_name: string;
  result: any;
}

// Workflow API Functions
export const workflowsAPI = {
  // Get all workflows
  getAll: async (): Promise<Workflow[]> => {
    return apiFetch<Workflow[]>('/workflows');
  },

  // Get workflow by name
  getByName: async (name: string): Promise<Workflow> => {
    return apiFetch<Workflow>(`/workflows/${name}`);
  },

  // Create workflow
  create: async (data: CreateWorkflowRequest): Promise<Workflow> => {
    return apiFetch<Workflow>('/workflows', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Update workflow
  update: async (name: string, data: UpdateWorkflowRequest): Promise<Workflow> => {
    return apiFetch<Workflow>(`/workflows/${name}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  // Delete workflow
  delete: async (name: string): Promise<void> => {
    return apiFetch<void>(`/workflows/${name}`, {
      method: 'DELETE',
    });
  },

  // Execute workflow
  execute: async (data: ExecuteWorkflowRequest): Promise<ExecuteWorkflowResponse> => {
    return apiFetch<ExecuteWorkflowResponse>(
      `/workflows/${data.workflow_name}/execute`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  },
};
