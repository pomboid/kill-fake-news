# ─── Build Stage ─────────────────────────────────────────────
FROM node:20-slim AS builder

WORKDIR /app

# Declare build arguments (passed from docker-compose)
ARG VITE_CLERK_PUBLISHABLE_KEY
ARG VITE_API_URL

# Make them available as environment variables during build
ENV VITE_CLERK_PUBLISHABLE_KEY=$VITE_CLERK_PUBLISHABLE_KEY
ENV VITE_API_URL=$VITE_API_URL

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# ─── Production Stage ─────────────────────────────────────────
FROM nginx:stable-alpine

COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx config to handle SPA routing if needed
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
