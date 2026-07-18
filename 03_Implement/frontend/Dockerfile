FROM node:20-alpine AS build
WORKDIR /app

# Public build-time contract key (KJ_ATLAS_* only)
ARG KJ_ATLAS_FRONTEND_API_BASE=/api
ARG KJ_ATLAS_RUNTIME_PROFILE=local-dev
ENV KJ_ATLAS_FRONTEND_API_BASE=${KJ_ATLAS_FRONTEND_API_BASE}
ENV KJ_ATLAS_RUNTIME_PROFILE=${KJ_ATLAS_RUNTIME_PROFILE}

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

FROM nginx:1.27-alpine
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
