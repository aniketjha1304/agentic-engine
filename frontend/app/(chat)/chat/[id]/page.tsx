// Chat page with dynamic ID
import { Chat as PreviewChat } from '@/components/chat';

// The main page component for dynamic route `/chat/[id]`
export default async function Page(props: { params: Promise<{ id: string }> }) {
  // Extracting the `id` from the dynamic route parameters
  const params = await props.params;
  const { id } = params;

  // Render the Chat component - it will load the chat data from the backend
  return (
    <PreviewChat
      id={id}
      initialMessages={[]}
    />
  );
}
