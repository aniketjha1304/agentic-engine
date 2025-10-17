import {
  type Message,
  StreamData,
  convertToCoreMessages,
  streamObject,
  streamText,
} from 'ai';
import { z } from 'zod';

import { auth } from '@/app/(auth)/auth';
import { customModel } from '@/lib/ai';
import { models } from '@/lib/ai/models';
import { systemPrompt } from '@/lib/ai/prompts';
import {
  deleteChatById,
  getChatById,
  saveChat,
  saveDocument,
  saveMessages,
  saveSuggestions,
} from '@/lib/db/queries';
import {
  generateUUID,
  getMostRecentUserMessage,
  sanitizeResponseMessages,
} from '@/lib/utils';

import { generateTitleFromUserMessage } from '../../actions';
import { Diagram } from 'mermaid/dist/Diagram.js';

export async function POST(request: Request) {
  const {
    id,
    messages,
    modelId,
  }: { id: string; messages: Array<Message>; modelId: string } =
    await request.json();

  const session = await auth();

  if (!session || !session.user || !session.user.id) {
    return new Response('Unauthorized', { status: 401 });
  }

  const model = models.find((model) => model.id === modelId);

  if (!model) {
    return new Response('Model not found', { status: 404 });
  }

  const coreMessages = convertToCoreMessages(messages);
  const userMessage = getMostRecentUserMessage(coreMessages);

  if (!userMessage) {
    return new Response('No user message found', { status: 400 });
  }

  const chat = await getChatById({ id });

  if (!chat) {
    const title = await generateTitleFromUserMessage({ message: userMessage });
    await saveChat({ id, userId: session.user.id, title });
  }

  await saveMessages({
    messages: [
      { ...userMessage, id: generateUUID(), createdAt: new Date(), chatId: id },
    ],
  });

  try {
    // Call the external FastAPI microservice
    const response = await fetch(`${process.env.LISA_ENGINE_URL}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        request: messages
      }),
    });

    if (!response.ok) {
      console.error('Failed to call lisa-engine:', await response.text());
      return new Response('Failed to process message', { status: 500 });
    }

    const lisaResponse = await response.json();

    console.log("Response from lisa-engine:", lisaResponse);

    // Check if the response contains a 'message' property
    if (!Array.isArray(lisaResponse.message)) {
      console.error('Unexpected response format from lisa-engine:', lisaResponse);
      return new Response('Invalid response format', { status: 500 });
    }

    // Process lisaResponse.message and create responseMessages
    const responseMessages = lisaResponse.message.map((message: any) => ({
      id: message.id || generateUUID(),
      chatId: id,
      role: message.role,
      content: JSON.stringify({ text: message.content, workflow: lisaResponse.workflow }),
      createdAt: message.createdAt ? new Date(message.createdAt) : new Date(),
    }));

    // Save messages with JSON content
    await saveMessages({
      messages: responseMessages,
    });

    // Return original response format for API response
    const responseForClient = lisaResponse.message.map((message: any) => ({
      id: message.id || generateUUID(),
      role: message.role,
      content: message.content,
      createdAt: message.createdAt ? new Date(message.createdAt) : new Date(),
      workflow: lisaResponse.workflow,
    }));

    return new Response(JSON.stringify(responseForClient), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error communicating with lisa-engine:', error);
    return new Response('Internal Server Error', { status: 500 });
  }
}


export async function DELETE(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');

  if (!id) {
    return new Response('Not Found', { status: 404 });
  }

  const session = await auth();

  if (!session || !session.user) {
    return new Response('Unauthorized', { status: 401 });
  }

  try {
    const chat = await getChatById({ id });

    if (chat.userId !== session.user.id) {
      return new Response('Unauthorized', { status: 401 });
    }

    await deleteChatById({ id });

    return new Response('Chat deleted', { status: 200 });
  } catch (error) {
    return new Response('An error occurred while processing your request', {
      status: 500,
    });
  }
}
