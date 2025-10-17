import { openai } from '@ai-sdk/openai';
// import { azure } from '@ai-sdk/azure';
import { experimental_wrapLanguageModel as wrapLanguageModel } from 'ai';
import { createAzure } from '@ai-sdk/azure';



import { customMiddleware } from './custom-middleware';

export const customModel = (apiIdentifier: string) => {
  const azure = createAzure({
    resourceName: 'recallspaceopenai'
  });
  return wrapLanguageModel({
    model: azure(apiIdentifier),
    middleware: customMiddleware,
  });
};
