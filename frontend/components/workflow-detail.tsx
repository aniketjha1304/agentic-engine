'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Editor from '@monaco-editor/react';
import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';
import { WorkflowIcon, CrossIcon } from '@/components/icons';
import type { Workflow } from '@/lib/api/chats';

interface WorkflowDetailProps {
  workflow: Workflow;
  onClose: () => void;
}

export function WorkflowDetail({ workflow, onClose }: WorkflowDetailProps) {
  const { theme } = useTheme();
  const [code, setCode] = useState(workflow.code);
  const [isEditing, setIsEditing] = useState(false);

  const handleSave = () => {
    // TODO: Implement save functionality when backend API is ready
    console.log('Saving workflow code:', code);
    setIsEditing(false);
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ x: '100%' }}
        animate={{ x: 0 }}
        exit={{ x: '100%' }}
        transition={{ type: 'spring', damping: 30, stiffness: 300 }}
        className="fixed right-0 top-0 h-full w-full md:w-2/3 lg:w-1/2 bg-background border-l shadow-2xl z-50 flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10 text-primary">
              <WorkflowIcon size={20} />
            </div>
            <div>
              <h2 className="font-semibold text-lg">{workflow.name}</h2>
              <p className="text-sm text-muted-foreground">
                {workflow.description || 'No description'}
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="h-8 w-8 p-0"
          >
            <CrossIcon />
          </Button>
        </div>

        {/* Metadata */}
        <div className="px-4 py-3 bg-muted/50 border-b space-y-2">
          {workflow.status && (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">Status:</span>
              <span className={`px-2 py-0.5 rounded-full text-xs ${
                workflow.status === 'active' 
                  ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300' 
                  : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
              }`}>
                {workflow.status}
              </span>
            </div>
          )}
          {workflow.endpoint && (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">Endpoint:</span>
              <code className="px-2 py-0.5 rounded bg-muted text-xs">
                {workflow.endpoint}
              </code>
            </div>
          )}
        </div>

        {/* Editor Controls */}
        <div className="flex items-center justify-between px-4 py-2 border-b bg-muted/30">
          <div className="text-sm font-medium text-muted-foreground">
            Python Code
          </div>
          <div className="flex gap-2">
            {isEditing ? (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setCode(workflow.code);
                    setIsEditing(false);
                  }}
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={handleSave}
                >
                  Save Changes
                </Button>
              </>
            ) : (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(true)}
              >
                Edit Code
              </Button>
            )}
          </div>
        </div>

        {/* Monaco Editor */}
        <div className="flex-1 overflow-hidden">
          <Editor
            height="100%"
            defaultLanguage="python"
            value={code}
            onChange={(value) => setCode(value || '')}
            theme={theme === 'dark' ? 'vs-dark' : 'light'}
            options={{
              readOnly: !isEditing,
              minimap: { enabled: true },
              fontSize: 14,
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 4,
              wordWrap: 'on',
            }}
          />
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
