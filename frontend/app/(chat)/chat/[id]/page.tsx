// Importing required utilities and components
import { cookies } from 'next/headers'; // Access cookies in the server environment
import { notFound } from 'next/navigation'; // Utility to render a 404-like "not found" page
import { auth } from '@/app/(auth)/auth'; // Authentication function to get the current user session
import { Chat as PreviewChat } from '@/components/chat'; // Chat component to render the chat UI
import { DEFAULT_MODEL_NAME, models } from '@/lib/ai/models'; // AI models and default model configuration
import { getChatById, getMessagesByChatId } from '@/lib/db/queries'; // Database queries for chat and messages
import { convertToUIMessages } from '@/lib/utils'; // Utility to transform DB messages into UI messages

// The main page component for dynamic route `/chat/[id]`
export default async function Page(props: { params: Promise<{ id: string }> }) {
  // Extracting the `id` from the dynamic route parameters
  const params = await props.params; // `params` is a promise, so it needs to be awaited
  const { id } = params;

  // Fetch the chat details by `id` from the database
  const chat = await getChatById({ id });

  // If the chat is not found, render a "not found" page
  if (!chat) {
    notFound();
  }

  // Fetch the authenticated user session
  const session = await auth();

  // If there is no authenticated user or the user session is invalid, render "not found"
  if (!session || !session.user) {
    return notFound();
  }

  // If the chat does not belong to the authenticated user, render "not found"
  if (session.user.id !== chat.userId) {
    return notFound();
  }

  // Fetch all messages related to the chat ID from the database
  const messagesFromDb = await getMessagesByChatId({
    id,
  });

  // Retrieve cookies from the request to get the user's selected model ID
  const cookieStore = await cookies(); // `cookies()` provides access to all cookies
  const modelIdFromCookie = cookieStore.get('model-id')?.value; // Retrieve the `model-id` cookie

  // Determine the selected model ID based on the cookie or default model
  const selectedModelId =
    models.find((model) => model.id === modelIdFromCookie)?.id || // Check if the cookie value matches a valid model ID
    DEFAULT_MODEL_NAME; // Fallback to the default model if no valid model is found

  // Render the `Chat` component with the required props
  return (
    <PreviewChat
      id={chat.id} // Pass the chat ID
      initialMessages={convertToUIMessages(messagesFromDb)} // Convert and pass the initial chat messages
      selectedModelId={selectedModelId} // Pass the selected AI model ID
    />
  );
}
