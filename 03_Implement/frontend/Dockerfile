FROM node:20-alpine AS build
WORKDIR /app

# Public build-time contract key (KJ_ATLAS_* only)
ARG KJ_ATLAS_FRONTEND_API_BASE=/api
ARG KJ_ATLAS_RUNTIME_PROFILE=local-dev
ARG KJ_ATLAS_APP_REVISION=unknown
ENV KJ_ATLAS_FRONTEND_API_BASE=${KJ_ATLAS_FRONTEND_API_BASE}
ENV KJ_ATLAS_RUNTIME_PROFILE=${KJ_ATLAS_RUNTIME_PROFILE}
# OPS-OBSERV-01 AC-4: baked into the built bundle so diagnostics report the
# actual revision instead of "unknown" in the standard Compose config.
ENV KJ_ATLAS_APP_REVISION=${KJ_ATLAS_APP_REVISION}

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

FROM nginx:1.27-alpine
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
