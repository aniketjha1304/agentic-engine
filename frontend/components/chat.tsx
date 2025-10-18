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
  const [chatId, setChatId] = useState(null);

  const [messagesContainerRef, messagesEndRef] = useScrollToBottom();

  useEffect(() => {
    if (selectedAgentName && !chatId) {
      createNewChat();
    }
  }, [selectedAgentName]);

  const createNewChat = async () => {
    if (!selectedAgentName) {
      toast.error('Please select an agent first');
      return;
    }
    try {
      const newChat = await chatsAPI.create({
        name: 'Chat with ' + selectedAgentName,
        agent_name: selectedAgentName,
      });
      setChatId(newChat.id);
    } catch (error) {
      toast.error(error.message || 'Failed to create chat');
    }
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!input.trim() || !selectedAgentName) {
      if (!selectedAgentName) toast.error('Please select an agent first');
      return;
    }
    if (!chatId) {
      await createNewChat();
      return;
    }
    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
      id: generateUUID(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    try {
      const response = await chatsAPI.sendMessage({
        chat_id: chatId,
        agent_name: selectedAgentName,
        message: input.trim(),
      });
      const assistantMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        id: generateUUID(),
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

  return (
    <div className="flex flex-col min-w-0 h-dvh bg-background">
      <ChatHeader selectedAgentName={selectedAgentName} onSelectAgent={onSelectAgent} />
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
