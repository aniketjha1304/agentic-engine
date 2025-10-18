'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useWindowSize } from 'usehooks-ts';

import { AgentSelector } from '@/components/agent-selector';
import { SidebarToggle } from '@/components/sidebar-toggle';
import { ThemeToggle } from '@/components/theme-toggle';
import { Button } from '@/components/ui/button';
import { BetterTooltip } from '@/components/ui/tooltip';
import { Input } from '@/components/ui/input';
import { PlusIcon, PencilEditIcon, CheckIcon } from './icons';
import { useSidebar } from './ui/sidebar';

export function ChatHeader({
  chatId,
  chatName,
  onRenameChat,
  selectedAgentName,
  onSelectAgent,
}: {
  chatId?: string | null;
  chatName?: string;
  onRenameChat?: (newName: string) => void;
  selectedAgentName?: string;
  onSelectAgent?: (agentName: string) => void;
}) {
  const router = useRouter();
  const { open } = useSidebar();
  const { width: windowWidth } = useWindowSize();
  
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(chatName || '');

  const handleSave = () => {
    if (onRenameChat && editValue.trim()) {
      onRenameChat(editValue.trim());
      setIsEditing(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      setEditValue(chatName || '');
      setIsEditing(false);
    }
  };

  return (
    <header className="flex sticky top-0 bg-background py-1.5 items-center px-2 md:px-2 gap-2">
      <SidebarToggle />
      {(!open || windowWidth < 768) && (
        <BetterTooltip content="New Chat">
          <Button
            variant="outline"
            className="order-2 md:order-1 md:px-2 px-2 md:h-fit ml-auto md:ml-0"
            onClick={() => {
              router.push('/');
              router.refresh();
            }}
          >
            <PlusIcon />
            <span className="md:sr-only">New Chat</span>
          </Button>
        </BetterTooltip>
      )}
      
      {/* Chat Title Editor */}
      {chatId && chatName && (
        <div className="flex items-center gap-2 order-1 md:order-2">
          {isEditing ? (
            <>
              <Input
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                onKeyDown={handleKeyDown}
                onBlur={handleSave}
                autoFocus
                className="h-8 w-48"
              />
              <Button
                size="sm"
                variant="ghost"
                onClick={handleSave}
                className="h-8 w-8 p-0"
              >
                <CheckIcon />
              </Button>
            </>
          ) : (
            <>
              <span className="text-sm font-medium truncate max-w-[200px]">{chatName}</span>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  setEditValue(chatName);
                  setIsEditing(true);
                }}
                className="h-8 w-8 p-0"
              >
                <PencilEditIcon />
              </Button>
            </>
          )}
        </div>
      )}
      
      <AgentSelector
        selectedAgentName={selectedAgentName}
        onSelectAgent={onSelectAgent}
        className={chatId ? "order-3" : "order-1 md:order-2"}
      />
      
      {/* Theme Toggle */}
      <div className={chatId ? "order-4 ml-auto" : "order-3 ml-auto"}>
        <ThemeToggle />
      </div>
    </header>
  );
}
