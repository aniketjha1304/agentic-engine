// workflow-block.tsx
import type {
  Attachment,
  ChatRequestOptions,
  CreateMessage,
  Message,
} from 'ai';
import { useEffect, useState, Dispatch, SetStateAction } from 'react';
import { motion } from 'framer-motion';
import dynamic from 'next/dynamic';
import { Button } from './ui/button';
import { CopyIcon, CrossIcon } from './icons';
import type { Workflow } from './workflow';
import { useWindowSize } from 'usehooks-ts';
import { useScrollToBottom } from './use-scroll-to-bottom';
import { MultimodalInput } from './multimodal-input';
import { PreviewMessage } from './message';
import { Toolbar } from './toolbar';
import { toast } from 'sonner';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';
import { useCopyToClipboard } from 'usehooks-ts';
import { AiOutlineEdit as EditIcon } from 'react-icons/ai'; // Edit icon
import { RiFlowChart as FlowchartIcon } from 'react-icons/ri';
import { WorkflowDiagram } from './workflow-diagram';

const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

export interface WorkflowBlockProps {
  workflow: Workflow;
  isVisible: boolean;
  boundingBox: {
    top: number;
    left: number;
    width: number;
    height: number;
  };
}

interface WorkflowBlockComponentProps {
  chatId: string;
  input: string;
  setInput: (input: string) => void;
  handleSubmit: (
    event?: {
      preventDefault?: () => void;
    },
    chatRequestOptions?: ChatRequestOptions,
  ) => void;
  isLoading: boolean;
  stop: () => void;
  attachments: Array<Attachment>;
  setAttachments: Dispatch<SetStateAction<Array<Attachment>>>;
  append: (
    message: Message | CreateMessage,
    chatRequestOptions?: ChatRequestOptions,
  ) => Promise<string | null | undefined>;
  messages: Array<Message>;
  setMessages: Dispatch<SetStateAction<Array<Message>>>;
  block: WorkflowBlockProps;
  setBlock: Dispatch<SetStateAction<WorkflowBlockProps>>;
}

export function WorkflowBlock({
  chatId,
  input,
  setInput,
  handleSubmit,
  isLoading,
  stop,
  attachments,
  setAttachments,
  append,
  messages,
  setMessages,
  block,
  setBlock,
}: WorkflowBlockComponentProps) {
  const { workflow, isVisible, boundingBox } = block;

  const [mode, setMode] = useState<'edit' | 'view'>('view');
  const [content, setContent] = useState(workflow.content);
  const [diagram, setDiagram] = useState(workflow.diagram);
  const [isToolbarVisible, setIsToolbarVisible] = useState(false); // Set to false initially

  const { width: windowWidth, height: windowHeight } = useWindowSize();
  const isMobile = windowWidth ? windowWidth < 768 : false;

  const [messagesContainerRef, messagesEndRef] = useScrollToBottom<HTMLDivElement>();

  const [_, copyToClipboard] = useCopyToClipboard();

  // Save content function
  const saveContent = async (updatedContent: string) => {
    try {
      await fetch(`/api/workflow?id=${workflow.id}`, {
        method: 'POST',
        body: JSON.stringify({
          ...workflow,
          content: updatedContent,
        }),
      });
      // Update the block's workflow content and preserve isVisible and other properties
      setBlock((prevBlock) => ({
        ...prevBlock,
        isVisible: true, // Ensure isVisible remains true
        workflow: {
          ...prevBlock.workflow,
          content: updatedContent,
          diagram: prevBlock.workflow.diagram, // Preserve diagram
        },
      }));
      toast.success('Workflow updated successfully');
    } catch (error) {
      console.error('Failed to save content:', error);
      toast.error('Failed to save content');
    }
  };

  const onContentChange = (value: string | undefined) => {
    setContent(value || '');
  };

  // Switch modes by clicking on icons
  const switchToEditMode = () => {
    setMode('edit');
  };

  const switchToViewMode = () => {
    saveContent(content);
    setMode('view');
  };

  const handleCopyToClipboard = () => {
    copyToClipboard(content);
    toast.success('Copied to clipboard!');
  };

  return (
    <motion.div
      className="flex flex-row h-dvh w-dvw fixed top-0 left-0 z-50 bg-muted"
      initial={{ opacity: 1 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, transition: { delay: 0.4 } }}
    >
      {!isMobile && (
        <motion.div
          className="relative w-[400px] bg-muted dark:bg-background h-dvh shrink-0"
          initial={{ opacity: 0, x: 10, scale: 1 }}
          animate={{
            opacity: 1,
            x: 0,
            scale: 1,
            transition: {
              delay: 0.2,
              type: 'spring',
              stiffness: 200,
              damping: 30,
            },
          }}
          exit={{
            opacity: 0,
            x: 0,
            scale: 0.95,
            transition: { delay: 0 },
          }}
        >
          <div className="flex flex-col h-full justify-between items-center gap-4">
            <div
              ref={messagesContainerRef}
              className="flex flex-col gap-4 h-full items-center overflow-y-scroll px-4 pt-20"
            >
              {messages.map((message, index) => (
                <PreviewMessage
                  chatId={chatId}
                  key={message.id}
                  message={message}
                  block={block}
                  setBlock={setBlock}
                  isLoading={isLoading && index === messages.length - 1}
                  vote={undefined}
                />
              ))}

              <div
                ref={messagesEndRef}
                className="shrink-0 min-w-[24px] min-h-[24px]"
              />
            </div>

            <form className="flex flex-row gap-2 relative items-end w-full px-4 pb-4">
              <MultimodalInput
                chatId={chatId}
                input={input}
                setInput={setInput}
                handleSubmit={handleSubmit}
                isLoading={isLoading}
                stop={stop}
                attachments={attachments}
                setAttachments={setAttachments}
                messages={messages}
                append={append}
                className="bg-background dark:bg-muted"
                setMessages={setMessages}
              />
            </form>
          </div>
        </motion.div>
      )}

      <motion.div
        className="fixed dark:bg-muted bg-background h-dvh flex flex-col shadow-xl overflow-y-scroll"
        initial={
          isMobile
            ? {
                opacity: 0,
                x: 0,
                y: 0,
                width: windowWidth,
                height: windowHeight,
                borderRadius: 50,
              }
            : {
                opacity: 0,
                x: boundingBox.left,
                y: boundingBox.top,
                height: boundingBox.height,
                width: boundingBox.width,
                borderRadius: 50,
              }
        }
        animate={
          isMobile
            ? {
                opacity: 1,
                x: 0,
                y: 0,
                width: windowWidth,
                height: '100dvh',
                borderRadius: 0,
                transition: {
                  delay: 0,
                  type: 'spring',
                  stiffness: 200,
                  damping: 30,
                },
              }
            : {
                opacity: 1,
                x: 400,
                y: 0,
                height: windowHeight,
                width: windowWidth ? windowWidth - 400 : 'calc(100dvw - 400px)',
                borderRadius: 0,
                transition: {
                  delay: 0,
                  type: 'spring',
                  stiffness: 200,
                  damping: 30,
                },
              }
        }
        exit={{
          opacity: 0,
          scale: 0.5,
          transition: {
            delay: 0.1,
            type: 'spring',
            stiffness: 600,
            damping: 30,
          },
        }}
      >
        <div className="p-2 flex flex-row justify-between items-center">
          <div className="flex flex-row items-start gap-4">
            <Button
              variant="outline"
              className="h-fit p-2 dark:hover:bg-zinc-700"
              onClick={() =>
                setBlock((currentBlock) => ({
                  ...currentBlock,
                  isVisible: false,
                }))
              }
            >
              <CrossIcon size={18} />
            </Button>

            <div className="flex flex-col">
              <div className="font-medium text-lg">{workflow.title}</div>
              <div className="text-sm text-muted-foreground">
                Status: {workflow.status || 'Development'}
              </div>
            </div>
          </div>

          <div className="flex flex-row gap-1">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant={mode === 'edit' ? 'default' : 'outline'}
                  className="p-2 h-fit dark:hover:bg-zinc-700"
                  onClick={switchToEditMode}
                >
                  <EditIcon size={18} />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Edit Code</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant={mode === 'view' ? 'default' : 'outline'}
                  className="p-2 h-fit dark:hover:bg-zinc-700"
                  onClick={switchToViewMode}
                >
                  <FlowchartIcon size={18} />
                </Button>
              </TooltipTrigger>
              <TooltipContent>View Diagram</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="outline"
                  className="p-2 h-fit dark:hover:bg-zinc-700"
                  onClick={handleCopyToClipboard}
                >
                  <CopyIcon size={18} />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Copy to clipboard</TooltipContent>
            </Tooltip>
          </div>
        </div>

        <div className="p-4 h-[calc(100vh-64px)] overflow-auto">
          {mode === 'edit' ? (
            <MonacoEditor
              height="100%"
              language="python" // Or the appropriate language
              value={content}
              onChange={onContentChange}
              theme="vs-dark"
            />
          ) : (
            // Use the WorkflowDiagram component
            workflow.diagram ? (
              <WorkflowDiagram nodes={workflow.diagram.nodes} edges={workflow.diagram.edges} />
            ) : (
              <div>Loading diagram...</div>
            )
          )}
        </div>

        {/* Include Toolbar */}
        <Toolbar
          isToolbarVisible={isToolbarVisible}
          setIsToolbarVisible={setIsToolbarVisible}
          append={append}
          isLoading={isLoading}
          stop={stop}
          setMessages={setMessages}
        />
      </motion.div>
    </motion.div>
  );
}