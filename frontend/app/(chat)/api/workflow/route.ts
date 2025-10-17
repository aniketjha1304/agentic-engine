// app/api/workflow/route.ts

import { auth } from '@/app/(auth)/auth';
import { getWorkflowById } from '@/lib/db/queries';
import AzureRepoConnector from '@/lib/azure-repo-connector';


export async function POST(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');

  if (!id) {
    return new Response('Missing id', { status: 400 });
  }

  // Authenticate the user
  const session = await auth();

  if (!session || !session.user) {
    return new Response('Unauthorized', { status: 401 });
  }

  // Get the workflow from the database
  const workflow = await getWorkflowById({ id });

  if (!workflow) {
    return new Response('Not Found', { status: 404 });
  }

  // Check if the workflow belongs to the authenticated user
//   if (workflow.userId !== session.user.id) {
//     return new Response('Unauthorized', { status: 401 });
//   }

  // Parse the request body to get the content
  const { content }: { content: string } = await request.json();

  if (!content) {
    return new Response('Missing content', { status: 400 });
  }

  // Generate the filename from the workflow title
  const filename = `${workflow.title.toLowerCase().replace(/\s+/g, '_')}`;
  const filePath = `/workflows/${filename}/${filename}.py`; // Adjust the path based on your repository structure

  // Initialize AzureRepoConnector
  const connector = new AzureRepoConnector();

  try {
    // Update the file in the Azure Repo
    await connector.updateFile(filePath, content);

    return Response.json( { status: 200 });
  } catch (error) {
    console.error('Failed to update workflow:', error);
    return new Response('Failed to update workflow', { status: 500 });
  }
}

export async function PATCH(request: Request) {
  // Implement PATCH method if needed
}

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');
  
    if (!id) {
      return new Response('Missing id', { status: 400 });
    }
  
    const session = await auth();
  
    if (!session || !session.user) {
      return new Response('Unauthorized', { status: 401 });
    }
  
    const workflow = await getWorkflowById({ id });
  
    if (!workflow) {
      return new Response('Not Found', { status: 404 });
    }
  
    if (workflow.userId !== session.user.id) {
      return new Response('Unauthorized', { status: 401 });
    }
  
    return Response.json(workflow, { status: 200 });
  }