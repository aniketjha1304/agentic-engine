'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useState } from 'react';
import { toast } from 'sonner';
import useSWR from 'swr';

import { MoreHorizontalIcon, TrashIcon } from '@/components/icons';
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar';
import { chatsAPI, type Chat } from '@/lib/api';

export function SidebarHistory() {
  const { setOpenMobile } = useSidebar();
  const { id } = useParams();
  const [deleteId, setDeleteId] = useState(null);

  const { data: chats = [], isLoading, mutate } = useSWR('chats', () => chatsAPI.getAll());

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await chatsAPI.delete(deleteId);
      toast.success('Chat deleted');
      mutate();
      setDeleteId(null);
    } catch (error) {
      toast.error(error.message || 'Failed to delete chat');
    }
  };

  if (isLoading) {
    return (
      <SidebarGroup>
        <SidebarGroupContent>
          <div className="px-2 py-1 text-xs text-muted-foreground">Loading...</div>
        </SidebarGroupContent>
      </SidebarGroup>
    );
  }

  if (chats.length === 0) {
    return (
      <SidebarGroup>
        <SidebarGroupContent>
          <div className="px-2 py-1 text-xs text-muted-foreground">
            No chats yet. Start a conversation!
          </div>
        </SidebarGroupContent>
      </SidebarGroup>
    );
  }

  return (
    <>
      <SidebarGroup>
        <SidebarGroupLabel>Chat History</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            {chats.map((chat) => (
              <SidebarMenuItem key={chat.id}>
                <SidebarMenuButton asChild isActive={chat.id === id}>
                  <Link href={`/chat/${chat.id}`} onClick={() => setOpenMobile(false)}>
                    <span>{chat.name}</span>
                  </Link>
                </SidebarMenuButton>
                <DropdownMenu modal={true}>
                  <DropdownMenuTrigger asChild>
                    <SidebarMenuAction
                      className="data-[state=open]:bg-sidebar-accent"
                      showOnHover={chat.id !== id}
                    >
                      <MoreHorizontalIcon />
                    </SidebarMenuAction>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent side="bottom" align="end">
                    <DropdownMenuItem
                      className="cursor-pointer text-destructive"
                      onSelect={() => setDeleteId(chat.id)}
                    >
                      <TrashIcon />
                      <span>Delete</span>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <AlertDialog open={!!deleteId} onOpenChange={(open) => !open && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Chat</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
