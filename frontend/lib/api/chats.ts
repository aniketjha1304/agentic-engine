import { apiFetch } from './config';

// Workflow Types
export interface Workflow {
  name: string;
  description: string;
  code: string;
  status?: string;
  endpoint?: string;
  input_parameters?: any;
  created_at?: string;
  updated_at?: string;
}

// Additional Data Types
export interface AdditionalData {
  workflows?: Workflow[];
  workflow?: Workflow;
  [key: string]: any; // Allow for future extensions
}

// Chat Types
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
  id?: string;
  additional_data?: AdditionalData;
}

export interface Chat {
  id: string;
  name: string;
  agent_name: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface CreateChatRequest {
  name: string;
  agent_name: string;
}

export interface SendMessageRequest {
  chat_id: string;
  agent_name: string;
  message: string;
}

export interface SendMessageResponse {
  message: string;
  chat_id: string;
  workflow?: any;
}

// Chat API Functions
export const chatsAPI = {
  // Get all chats
  getAll: async (): Promise<Chat[]> => {
    return apiFetch<Chat[]>('/chats');
  },

  // Get chat by ID
  getById: async (chatId: string): Promise<Chat> => {
    return apiFetch<Chat>(`/chats/${chatId}`);
  },

  // Create chat
  create: async (data: CreateChatRequest): Promise<Chat> => {
    return apiFetch<Chat>('/chats', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Update chat
  update: async (
    chatId: string,
    params: { name?: string; agent_name?: string }
  ): Promise<Chat> => {
    const queryParams = new URLSearchParams();
    if (params.name) queryParams.set('name', params.name);
    if (params.agent_name) queryParams.set('agent_name', params.agent_name);

    return apiFetch<Chat>(`/chats/${chatId}?${queryParams.toString()}`, {
      method: 'PUT',
    });
  },

  // Delete chat
  delete: async (chatId: string): Promise<void> => {
    return apiFetch<void>(`/chats/${chatId}`, {
      method: 'DELETE',
    });
  },

  // Send message to agent
  sendMessage: async (data: SendMessageRequest): Promise<SendMessageResponse> => {
    return apiFetch<SendMessageResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};
