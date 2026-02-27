# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Copy only package files to leverage Docker cache
COPY package*.json ./

# Install dependencies, including devDependencies needed for build
RUN npm ci

# Copy the rest of the application code
COPY . .

# Build Next.js application
RUN npm run build

# Stage 2: Production
FROM node:20-alpine AS runner

WORKDIR /app

# Copy only production dependencies and the build output
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

USER nextjs

# Expose the default Next.js port
EXPOSE 3000

# Start the Next.js server
CMD ["npm", "start"]
