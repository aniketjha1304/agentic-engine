'use client';

import { useState } from 'react';
import { Chat } from '@/components/chat';

export default function Page() {
  const [selectedAgent, setSelectedAgent] = useState<string>('');

  return (
    <Chat
      id=""
      initialMessages={[]}
      selectedAgentName={selectedAgent}
      onSelectAgent={setSelectedAgent}
    />
  );
}
