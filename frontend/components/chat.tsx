'use client';

import type { Attachment } from 'ai';
import { useState, useEffect } from 'react';
import { toast } from 'sonner';

import { ChatHeader } from '@/components/chat-header';
import { PreviewMessage, ThinkingMessage } from '@/components/message';
import { useScrollToBottom } from '@/components/use-scroll-to-bottom';
import { MultimodalInput } from './multimodal-input';
import { Overview } from './overview';
import { chatsAPI, type ChatMessage } from '@/lib/api';
import { generateUUID } from '@/lib/utils';

export function Chat({
  id,
  initialMessages,
  selectedAgentName,
  onSelectAgent,
}: {
  id: string;
  initialMessages: ChatMessage[];
  selectedAgentName?: string;
  onSelectAgent?: (agentName: string) => void;
}) {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [attachments, setAttachments] = useState([]);
  const [chatId, setChatId] = useState(id || null);
  const [chatName, setChatName] = useState('');
  const [loadError, setLoadError] = useState(false);

  const [messagesContainerRef, messagesEndRef] = useScrollToBottom();

  // Load existing chat if ID is provided
  useEffect(() => {
    if (id && id.trim() !== '' && !loadError) {
      setChatId(id);
      loadChat(id);
    } else if (!id || id.trim() === '') {
      // New chat, clear everything
      setChatId(null);
      setMessages([]);
      setChatName('');
      setLoadError(false);
    }
  }, [id]);

  const loadChat = async (chatId: string) => {
    try {
      const chat = await chatsAPI.getById(chatId);
      setMessages(chat.messages || []);
      setChatName(chat.name);
      setLoadError(false);
      // Set the agent from the chat if not already selected
      if (onSelectAgent && chat.agent_name) {
        onSelectAgent(chat.agent_name);
      }
    } catch (error) {
      setLoadError(true);
      toast.error('Chat not found');
      // Don't auto-redirect, just show error state
    }
  };

  const createNewChat = async () => {
    if (!selectedAgentName) {
      toast.error('Please select an agent first');
      return null;
    }
    try {
      const newChat = await chatsAPI.create({
        name: 'Chat with ' + selectedAgentName,
        agent_name: selectedAgentName,
      });
      setChatId(newChat.id);
      setChatName(newChat.name);
      // Update URL to the new chat
      window.history.replaceState({}, '', `/chat/${newChat.id}`);
      return newChat.id;
    } catch (error) {
      toast.error(error.message || 'Failed to create chat');
      return null;
    }
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!input.trim() || !selectedAgentName) {
      if (!selectedAgentName) toast.error('Please select an agent first');
      return;
    }
    
    // Create chat on first message if doesn't exist
    let currentChatId = chatId;
    if (!currentChatId) {
      currentChatId = await createNewChat();
      if (!currentChatId) return;
    }
    const userMessage = {
      role: 'user' as const,
      content: input.trim(),
      timestamp: new Date().toISOString(),
      id: generateUUID(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    try {
      const response = await chatsAPI.sendMessage({
        chat_id: currentChatId,
        agent_name: selectedAgentName,
        message: input.trim(),
      });
      const assistantMessage: ChatMessage = {
        role: 'assistant' as const,
        content: response.message,
        timestamp: new Date().toISOString(),
        id: generateUUID(),
        additional_data: response.additional_data,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      toast.error(error.message || 'Failed to send message');
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const stop = () => setIsLoading(false);

  const handleRenameChat = async (newName: string) => {
    if (!chatId || !newName.trim()) return;
    try {
      await chatsAPI.update(chatId, { name: newName.trim() });
      setChatName(newName.trim());
      toast.success('Chat renamed successfully');
    } catch (error) {
      toast.error('Failed to rename chat');
    }
  };

  if (loadError) {
    return (
      <div className="flex flex-col min-w-0 h-dvh bg-background">
        <ChatHeader 
          selectedAgentName={selectedAgentName} 
          onSelectAgent={onSelectAgent} 
        />
        <div className="flex flex-col items-center justify-center flex-1 gap-4">
          <p className="text-xl font-semibold">Chat not found</p>
          <p className="text-muted-foreground">This chat may have been deleted.</p>
          <a href="/" className="text-primary hover:underline">Go to home</a>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-w-0 h-dvh bg-background">
      <ChatHeader 
        chatId={chatId} 
        chatName={chatName}
        onRenameChat={handleRenameChat}
        selectedAgentName={selectedAgentName} 
        onSelectAgent={onSelectAgent} 
      />
      <div ref={messagesContainerRef} className="flex flex-col min-w-0 gap-6 flex-1 overflow-y-scroll pt-4">
        {messages.length === 0 && <Overview />}
        {messages.map((message, index) => (
          <PreviewMessage key={message.id || index} chatId={chatId || ''} message={message} isLoading={isLoading && messages.length - 1 === index} />
        ))}
        {isLoading && messages.length > 0 && messages[messages.length - 1].role === 'user' && <ThinkingMessage />}
        <div ref={messagesEndRef} className="shrink-0 min-w-[24px] min-h-[24px]" />
      </div>
      <form className="flex mx-auto px-4 bg-background pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
        <MultimodalInput chatId={chatId || ''} input={input} setInput={setInput} handleSubmit={handleSubmit} isLoading={isLoading} stop={stop} attachments={attachments} setAttachments={setAttachments} />
      </form>
    </div>
  );
}
