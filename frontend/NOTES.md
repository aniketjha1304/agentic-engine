- We are using normal login functinaity from next.js and use basic credentials stuff.
- the authentication is spcificed in auth.ts and routes are in api
- Read more about the authentication in next.js


- Once after login the main page becomes the (chat).page.tsx
- The useChat from ai sdk of vercel helps to create chat interfaces in easy way.
- There are two partsone is useChat for components and stuff which maintain the ui based on responses and stuff
other is the streamText... which is communicating with the llm providers.
- I make a difference in implementation by using onResponse and then will override the api/chat with communication to lisa.


## Deploying a Next.js Application with Docker on Azure Container Apps
 
This guide provides a comprehensive summary of deploying a Next.js application using Docker on Azure Container Apps. It includes the step-by-step process, issues encountered during deployment, their fixes, and fundamental concepts related to Next.js deployment.

### Table of Contents
 

Introduction
Prerequisites
Deployment Steps
1. Containerizing the Next.js Application
2. Building and Testing the Docker Image Locally
3. Pushing the Docker Image to a Container Registry
4. Deploying to Azure Container Apps
5. Setting Environment Variables
6. Handling Database Migrations
Issues Faced and Their Fixes
Issue 1: Missing package-lock.json
Issue 2: pnpm Not Found
Issue 3: Error During Build - POSTGRES_URL Not Defined
Issue 4: Missing next.config.js
Issue 5: tsx Not Found in Runtime
Issue 6: Outdated pnpm-lock.yaml
Issue 7: Environment Variables Not Recognized in Runtime
Issue 8: Authentication Error - UntrustedHost
Fundamental Concepts
package.json
npm and pnpm
Build Steps in Next.js
Understanding Dockerfile and Multi-stage Builds
Conclusion
References
Introduction
 
Deploying a Next.js application involves several steps, from containerizing the application to managing environment variables and ensuring the application runs smoothly in the production environment. This guide walks through the process of deploying a Next.js application using Docker and Azure Container Apps, highlighting common issues and their solutions.

### Prerequisites
 

Azure Account: An active Azure account.
Azure CLI: Installed and configured. Install Azure CLI.
Docker: Installed on your local machine. Install Docker.
Next.js Application: Your Next.js application ready for deployment.
Container Registry: Azure Container Registry or Docker Hub account for storing Docker images.
Deployment Steps
 

1. Containerizing the Next.js Application
 
Create a Dockerfile in the root directory of your Next.js project to containerize your application.

Sample Dockerfile:
```docker

# Install dependencies only when needed  
FROM node:18-alpine AS deps  
WORKDIR /app  
  
# Install pnpm globally  
RUN npm install -g pnpm  
  
# Copy package.json and pnpm-lock.yaml  
COPY package.json pnpm-lock.yaml ./  
  
# Install dependencies  
RUN pnpm install --frozen-lockfile  
  
# Rebuild the source code only when needed  
FROM node:18-alpine AS builder  
WORKDIR /app  
  
# Install pnpm globally  
RUN npm install -g pnpm  
  
# Copy all files and folders  
COPY . .  
  
# Copy node_modules from deps  
COPY --from=deps /app/node_modules ./node_modules  
  
# Build the Next.js application  
RUN pnpm build  
  
# Production image, copy all the files and run the application  
FROM node:18-alpine AS runner  
WORKDIR /app  
  
# Set NODE_ENV to production  
ENV NODE_ENV=production  
  
# Install pnpm globally  
RUN npm install -g pnpm  
  
# Copy necessary files from builder  
COPY --from=builder /app/public ./public  
COPY --from=builder /app/.next ./.next  
COPY --from=builder /app/package.json ./  
COPY --from=builder /app/lib ./lib  
  
# Install only production dependencies  
RUN pnpm install --prod --no-dev  
  
# Expose the port  
EXPOSE 3000  
  
# Start the Next.js app  
CMD ["pnpm", "start"]  
```

2. Building and Testing the Docker Image Locally

Build the Docker Image:

```
docker build -t lisa-app:latest .  
```
Run the Docker Image Locally:

```
docker run -p 3000:3000 lisa-app:latest
```
Visit http://localhost:3000 to verify the app is running.

3. Pushing the Docker Image to a Container Registry
 
Option A: Using Azure Container Registry

Login to ACR:


az acr login --name recallcontainers.azurecr.io
 
Tag and Push the Image:

```                                                                                                              
docker tag lisa-app:latest recallcontainers.azurecr.io/lisa-app:latest
docker push recallcontainers.azurecr.io/lisa-app:latest    
```

 

4. Setting Environment Variables
 
Set necessary environment variables such as POSTGRES_URL, NEXTAUTH_URL, and NEXTAUTH_SECRET either through Azure CLI or Azure Portal.
```
POSTGRES_URL
NEXTAUTH_URL
NEXTAUTH_SECRET
AZURE_API_KEY
OPENAI_API_KEY
LISA_ENGINE_URL
AUTH_TRUST_HOST
```

5. Handling Database Migrations
 
Run database migrations at runtime rather than during the Docker build process.

Adjust the Migration Script:

Modify the script to load environment variables appropriately and avoid loading dotenv in production environments.


if (process.env.NODE_ENV !== 'production') {  
  config({  
    path: '.env.local',  
  });  
}  
 
Modify the Dockerfile to Copy Necessary Files:

Ensure that the lib directory and migration scripts are included in the Docker image.


COPY --from=builder /app/lib ./lib  
 

Issues Faced and Their Fixes
 

Issue 1: Missing package-lock.json
 
Error:


ERROR: failed to compute cache key: "/package-lock.json": not found  
 
Cause: The Dockerfile tried to copy package-lock.json, which didn't exist.

Fix: Adjust the COPY command to use pnpm-lock.yaml and update the Dockerfile to work with pnpm instead of npm.


COPY package.json pnpm-lock.yaml ./  
 
 

Issue 2: pnpm Not Found
 
Error:


/bin/sh: pnpm: not found  
 
Cause: pnpm was not installed in the Docker image.

Fix: Install pnpm globally in the Docker image by adding the following line to the Dockerfile in each stage where pnpm is used:


RUN npm install -g pnpm  
 
 

Issue 3: Error During Build - POSTGRES_URL Not Defined
 
Error:


Error: POSTGRES_URL is not defined  
 
Cause: The build process attempted to run database migrations which required the POSTGRES_URL environment variable.

Fix: Remove migrations from the build process. Adjust the package.json scripts to separate the migration command and run migrations at runtime instead.


"scripts": {  
  "build": "next build",  
  "migrate": "tsx lib/db/migrate",  
  // other scripts...  
}  
 
 

Issue 4: Missing next.config.js
 
Error:


ERROR: failed to compute cache key: "/app/next.config.js": not found  
 
Cause: The Dockerfile attempted to copy next.config.js, which didn't exist.

Fix: Remove the COPY command for next.config.js in the Dockerfile.


# Remove or comment out the following line  
# COPY --from=builder /app/next.config.js ./  
 
 

Issue 5: tsx Not Found in Runtime
 
Error:


sh: tsx: not found  
 
Cause: tsx was listed under devDependencies and not available in the production environment.

Fix: Move tsx to dependencies in package.json to ensure it is installed in the production environment.


"dependencies": {  
  "tsx": "^4.19.1",  
  // other dependencies...  
},  
"devDependencies": {  
  // dev dependencies...  
}  
 
 

Issue 6: Outdated pnpm-lock.yaml
 
Error:


ERR_PNPM_OUTDATED_LOCKFILE Cannot install with "frozen-lockfile" because pnpm-lock.yaml is not up to date  
 
Cause: The pnpm-lock.yaml was out of sync with package.json.

Fix: Run pnpm install locally to update the lockfile and then rebuild the Docker image.


pnpm install  
docker build -t yourusername/yourappname:latest .  
 
 

Issue 7: Environment Variables Not Recognized in Runtime
 
Error:


Error: POSTGRES_URL is not defined  
 
Cause: The migration script was using dotenv to load environment variables, possibly overriding the environment variables set in the container.

Fix: Modify the migration script to load dotenv only in development environments.


if (process.env.NODE_ENV !== 'production') {  
  config({  
    path: '.env.local',  
  });  
}  
 
 

Issue 8: Authentication Error - UntrustedHost
 
Error:


[auth][error] UntrustedHost: Host must be trusted. URL was: https://your-app.azurecontainerapps.io/api/auth/session.  
 
Cause: NextAuth.js detected that the incoming request's host did not match the trusted hosts.

Fix: Set the NEXTAUTH_URL environment variable to the application's public URL and add trustHost: true in the NextAuth.js configuration.

Set NEXTAUTH_URL:


az containerapp update \  
  --name yourAppName \  
  --resource-group yourResourceGroup \  
  --environment-variables \  
    NEXTAUTH_URL=https://your-app-url  
 
Update NextAuth.js Configuration:


export default NextAuth({  
  ...authConfig,  
  // other configurations...  
  trustHost: true,  
});  
 
Security Consideration: Setting trustHost: true can have security implications. Consider using a custom domain or configuring Azure Container Apps to use a stable URL.

Fundamental Concepts
 

package.json
 

Definition: A file that holds various metadata relevant to the project. It lists the project's dependencies, scripts, version, and other configurations.
Purpose: Used by package managers like npm and pnpm to install dependencies and run project scripts.
npm and pnpm
 

npm: The default package manager for Node.js projects. It installs packages and manages dependencies.
pnpm: An alternative package manager for Node.js that uses disk space efficiently by storing dependencies in a global store and creating hard links.
Build Steps in Next.js
 

Purpose of Building: The build process compiles the Next.js application, optimizing it for production by generating server-rendered pages and static assets.
Steps Involved:
Running next build to compile the application.
Generating the .next directory containing the build output.
Understanding Dockerfile and Multi-stage Builds
 

Dockerfile: A script containing instructions to build a Docker image, specifying the environment and commands to execute.
Multi-stage Builds: A Dockerfile feature that allows using multiple FROM statements to create images in stages, optimizing the final image size.
Stages in the Provided Dockerfile:
deps Stage: Installs dependencies.
builder Stage: Copies the source code and builds the application.
runner Stage: Prepares the production image, copying necessary files and installing production dependencies.
Conclusion
 
Deploying a Next.js application using Docker on Azure Container Apps involves containerizing the application, handling environment variables, and addressing issues that arise during the process. Understanding the fundamental concepts of package management, the build process, and Docker configurations is crucial for a successful deployment.

References
 

Next.js Documentation
Docker Documentation
Azure Container Apps Documentation
pnpm Documentation
NextAuth.js Documentation