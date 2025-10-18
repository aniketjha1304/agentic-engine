'use client';

import { useState } from 'react';
import { Chat } from '@/components/chat';
import { generateUUID } from '@/lib/utils';

export default function Page() {
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const id = generateUUID();

  return (
    <Chat
      key={id}
      id={id}
      initialMessages={[]}
      selectedAgentName={selectedAgent}
      onSelectAgent={setSelectedAgent}
    />
  );
}
