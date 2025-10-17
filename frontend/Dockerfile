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

# Production image, copy all the files and run next
FROM node:18-alpine AS runner
WORKDIR /app
# Added because the envirom=nment variable is referenced in migration scripts
ENV NODE_ENV=production

# Install pnpm globally
RUN npm install -g pnpm
# Tsk is required to run the subscription
RUN npm install -g tsx

# Copy necessary files from builder
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package.json ./
COPY --from=builder /app/next.config.ts ./
# Copy the lib directory (includes your migration script)
COPY --from=builder /app/lib ./lib
# Install only production dependencies
RUN pnpm install --prod --no-dev

# Expose the port
EXPOSE 3000
# Start the Next.js app
# to ensure migration errors are visible and do not silently fail:
CMD ["sh", "-c", "pnpm migrate || exit 1 && pnpm start"]