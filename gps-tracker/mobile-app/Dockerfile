# Flutter Web App Dockerfile - Multi-stage build

# Stage 1: Build Flutter web app
FROM debian:bullseye-slim AS build

# Install Flutter dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

# Install Flutter
ENV FLUTTER_VERSION=3.24.5
ENV FLUTTER_HOME=/opt/flutter
RUN git clone --depth 1 --branch ${FLUTTER_VERSION} https://github.com/flutter/flutter.git ${FLUTTER_HOME}
ENV PATH="${FLUTTER_HOME}/bin:${PATH}"

# Pre-download Flutter dependencies
RUN flutter doctor -v
RUN flutter config --enable-web

# Copy Flutter project
WORKDIR /app
COPY ble_tracker_app/pubspec.yaml ble_tracker_app/pubspec.lock ./
RUN flutter pub get

# Copy rest of the project
COPY ble_tracker_app ./

# Build Flutter web app
RUN flutter build web --release --base-href="/"

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy Flutter web build from build stage
COPY --from=build /app/build/web /usr/share/nginx/html

# Copy custom nginx configuration for Flutter web app
RUN echo 'server {' > /etc/nginx/conf.d/default.conf && \
    echo '    listen 80;' >> /etc/nginx/conf.d/default.conf && \
    echo '    server_name localhost;' >> /etc/nginx/conf.d/default.conf && \
    echo '    root /usr/share/nginx/html;' >> /etc/nginx/conf.d/default.conf && \
    echo '    index index.html;' >> /etc/nginx/conf.d/default.conf && \
    echo '' >> /etc/nginx/conf.d/default.conf && \
    echo '    # Serve Flutter web app' >> /etc/nginx/conf.d/default.conf && \
    echo '    location / {' >> /etc/nginx/conf.d/default.conf && \
    echo '        try_files $uri $uri/ /index.html;' >> /etc/nginx/conf.d/default.conf && \
    echo '    }' >> /etc/nginx/conf.d/default.conf && \
    echo '' >> /etc/nginx/conf.d/default.conf && \
    echo '    # Handle Flutter service worker' >> /etc/nginx/conf.d/default.conf && \
    echo '    location /flutter_service_worker.js {' >> /etc/nginx/conf.d/default.conf && \
    echo '        add_header Cache-Control "no-cache, no-store, must-revalidate";' >> /etc/nginx/conf.d/default.conf && \
    echo '    }' >> /etc/nginx/conf.d/default.conf && \
    echo '}' >> /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
