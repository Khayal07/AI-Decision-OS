# Web image (build context: repo root, monorepo-aware)
FROM node:22-slim

WORKDIR /repo

RUN npm install -g pnpm@11.9.0

# Install deps from the lockfile (workspace manifests first for better caching)
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml turbo.json ./
COPY apps/web/package.json ./apps/web/package.json
RUN pnpm install --frozen-lockfile

# Build the web app
COPY . .
RUN pnpm --filter @ai-decision-os/web build

ENV NODE_ENV=production
EXPOSE 3000

CMD ["pnpm", "--filter", "@ai-decision-os/web", "start"]
