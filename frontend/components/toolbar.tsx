// toolbar.tsx
'use client';

import type { ChatRequestOptions, CreateMessage, Message } from 'ai';
import cx from 'classnames';
import { AnimatePresence, motion } from 'framer-motion';
import {
  Dispatch,
  SetStateAction,
  useEffect,
  useRef,
  useState,
} from 'react';
import { useOnClickOutside } from 'usehooks-ts';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from './ui/tooltip';

import {
  AiOutlineSetting as SettingsIcon,
  AiOutlineMonitor as ReviewIcon,
  AiOutlineCloudUpload as PushIcon,
  AiOutlineSave as SaveIcon,
  AiOutlineClose as StopIcon,
  AiOutlinePlus as MoreActionsIcon,
} from 'react-icons/ai';

type ToolType = 'main' | 'configure-env' | 'review-logic' | 'push-workflow' | 'save-code';

type ToolProps = {
  type: ToolType;
  description: string;
  icon: JSX.Element;
  selectedTool: ToolType | null;
  setSelectedTool: Dispatch<SetStateAction<ToolType | null>>;
  isToolbarVisible?: boolean;
  setIsToolbarVisible?: Dispatch<SetStateAction<boolean>>;
  isAnimating: boolean;
  append?: (
    message: Message | CreateMessage,
    chatRequestOptions?: ChatRequestOptions,
  ) => Promise<string | null | undefined>;
};

const Tool = ({
  type,
  description,
  icon,
  selectedTool,
  setSelectedTool,
  isToolbarVisible,
  setIsToolbarVisible,
  isAnimating,
  append,
}: ToolProps) => {
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    if (selectedTool !== type) {
      setIsHovered(false);
    }
  }, [selectedTool, type]);

  const handleSelect = () => {
    if (type === 'main' && setIsToolbarVisible) {
      // Toggle the toolbar visibility when the main button is clicked
      setIsToolbarVisible(!isToolbarVisible);
      return;
    }

    // For other tools, implement the actual logic
    if (append) {
      if (type === 'configure-env') {
        // TODO: Implement logic for configuring environment variables
        append({
          role: 'user',
          content: 'Configure the environment variables for this workflow.',
        });
      } else if (type === 'review-logic') {
        // TODO: Implement logic for reviewing workflow logic
        append({
          role: 'user',
          content: 'Review the workflow logic and provide feedback.',
        });
      } else if (type === 'push-workflow') {
        // TODO: Implement logic for pushing the workflow to the next environment
        append({
          role: 'user',
          content: 'Push the workflow to the next environment.',
        });
      } else if (type === 'save-code') {
        // TODO: Implement logic for saving the code
        append({
          role: 'user',
          content: 'Save the current code changes.',
        });
      }
    }

    setSelectedTool(null);
    // Close the toolbar after selecting an action
    if (setIsToolbarVisible) {
      setIsToolbarVisible(false);
    }
  };

  return (
    <Tooltip open={isHovered && !isAnimating} delayDuration={0}>
      <TooltipTrigger asChild>
        <motion.div
          className={cx('p-3 rounded-full', {
            'bg-primary text-primary-foreground': selectedTool === type,
          })}
          onHoverStart={() => {
            setIsHovered(true);
          }}
          onHoverEnd={() => {
            if (selectedTool !== type) setIsHovered(false);
          }}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              handleSelect();
            }
          }}
          initial={{ scale: 1, opacity: 0 }}
          animate={{ opacity: 1 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          exit={{
            scale: 0.9,
            opacity: 0,
            transition: { duration: 0.1 },
          }}
          onClick={handleSelect}
        >
          {icon}
        </motion.div>
      </TooltipTrigger>
      <TooltipContent
        side="left"
        sideOffset={16}
        className="bg-foreground text-background rounded-2xl p-3 px-4"
      >
        {description}
      </TooltipContent>
    </Tooltip>
  );
};

export const Tools = ({
  isToolbarVisible,
  selectedTool,
  setSelectedTool,
  append,
  isAnimating,
  setIsToolbarVisible,
}: {
  isToolbarVisible: boolean;
  selectedTool: ToolType | null;
  setSelectedTool: Dispatch<SetStateAction<ToolType | null>>;
  append?: (
    message: Message | CreateMessage,
    chatRequestOptions?: ChatRequestOptions,
  ) => Promise<string | null | undefined>;
  isAnimating: boolean;
  setIsToolbarVisible: Dispatch<SetStateAction<boolean>>;
}) => {
  return (
    <motion.div
      className="flex flex-col items-center"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
    >
      <AnimatePresence>
        {isToolbarVisible && (
          <motion.div
            key="tools-list"
            className="flex flex-col items-center"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
          >
            <Tool
              type="configure-env"
              description="Configure Environment Variables"
              icon={<SettingsIcon size={20} />}
              selectedTool={selectedTool}
              setSelectedTool={setSelectedTool}
              append={append}
              isAnimating={isAnimating}
            />

            <Tool
              type="review-logic"
              description="Review Workflow Logic"
              icon={<ReviewIcon size={20} />}
              selectedTool={selectedTool}
              setSelectedTool={setSelectedTool}
              append={append}
              isAnimating={isAnimating}
            />

            <Tool
              type="push-workflow"
              description="Push Workflow to Next Environment"
              icon={<PushIcon size={20} />}
              selectedTool={selectedTool}
              setSelectedTool={setSelectedTool}
              append={append}
              isAnimating={isAnimating}
            />

            <Tool
              type="save-code"
              description="Save Code"
              icon={<SaveIcon size={20} />}
              selectedTool={selectedTool}
              setSelectedTool={setSelectedTool}
              append={append}
              isAnimating={isAnimating}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Tool Button to Open the Toolbar */}
      <Tool
        type="main"
        description="Actions"
        icon={<MoreActionsIcon size={18} />}
        selectedTool={selectedTool}
        setSelectedTool={setSelectedTool}
        isToolbarVisible={isToolbarVisible}
        setIsToolbarVisible={setIsToolbarVisible}
        isAnimating={isAnimating}
      />
    </motion.div>
  );
};

export const Toolbar = ({
  isToolbarVisible,
  setIsToolbarVisible,
  append,
  isLoading,
  stop,
  setMessages,
}: {
  isToolbarVisible: boolean;
  setIsToolbarVisible: Dispatch<SetStateAction<boolean>>;
  isLoading: boolean;
  append?: (
    message: Message | CreateMessage,
    chatRequestOptions?: ChatRequestOptions,
  ) => Promise<string | null | undefined>;
  stop?: () => void;
  setMessages?: Dispatch<SetStateAction<Message[]>>;
}) => {
  const toolbarRef = useRef<HTMLDivElement>(null);

  const [selectedTool, setSelectedTool] = useState<ToolType | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);

  useOnClickOutside(toolbarRef, () => {
    setIsToolbarVisible(false);
    setSelectedTool(null);
  });

  useEffect(() => {
    if (isLoading) {
      setIsToolbarVisible(false);
    }
  }, [isLoading, setIsToolbarVisible]);

  return (
    <TooltipProvider delayDuration={0}>
      <motion.div
        className="cursor-pointer fixed right-6 bottom-6 p-1.5 border rounded-full shadow-lg bg-background flex flex-col items-center"
        initial={{ opacity: 0, y: -20, scale: 1 }}
        animate={{
          opacity: 1,
          y: 0,
          height: 'auto',
          transition: { delay: 0 },
          scale: 1,
        }}
        exit={{ opacity: 0, y: -20, transition: { duration: 0.1 } }}
        transition={{ type: 'spring', stiffness: 300, damping: 25 }}
        ref={toolbarRef}
      >
        {isLoading ? (
          <motion.div
            key="stop-icon"
            initial={{ scale: 1 }}
            animate={{ scale: 1.4 }}
            exit={{ scale: 1 }}
            className="p-3"
            onClick={() => {
              if (stop) {
                stop();
                // TODO: Handle stopping the current process
              }
            }}
          >
            <StopIcon size={24} />
          </motion.div>
        ) : (
          <Tools
            key="tools"
            append={append}
            isAnimating={isAnimating}
            isToolbarVisible={isToolbarVisible}
            selectedTool={selectedTool}
            setIsToolbarVisible={setIsToolbarVisible}
            setSelectedTool={setSelectedTool}
          />
        )}
      </motion.div>
    </TooltipProvider>
  );
};