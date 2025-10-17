// Import the `cookies` utility from Next.js to handle HTTP cookies
import { cookies } from 'next/headers';

// Import the Chat component, which handles the chat UI and logic
import { Chat } from '@/components/chat';

// Import default model configurations for the AI system
import { DEFAULT_MODEL_NAME, models } from '@/lib/ai/models';

// Utility to generate a unique ID (e.g., for tracking user sessions or chat instances)
import { generateUUID } from '@/lib/utils';

// Async function to define the page component
export default async function Page() {
  console.log("This is app/(chat)/page.tsx")
  // Generate a unique identifier for this chat session
  const id = generateUUID();

  // Access the cookies stored in the user's browser
  const cookieStore = await cookies();

  // Get the value of the 'model-id' cookie if it exists
  const modelIdFromCookie = cookieStore.get('model-id')?.value;

  // Determine the selected model ID:
  // 1. If a valid model ID exists in cookies, use it.
  // 2. Otherwise, fall back to the default model name.
  const selectedModelId =
    models.find((model) => model.id === modelIdFromCookie)?.id ||
    DEFAULT_MODEL_NAME;

  // Render the Chat component with initial props:
  // - `key`: Ensures React treats each chat instance as unique.
  // - `id`: Passes the unique session ID.
  // - `initialMessages`: Starts with an empty message history.
  // - `selectedModelId`: Specifies the selected AI model.
  return (
    <Chat
      key={id}
      id={id}
      initialMessages={[]}
      selectedModelId={selectedModelId}
    />
  );
}
