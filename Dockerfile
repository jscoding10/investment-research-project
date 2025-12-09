# Multi-stage: Build Angular → Serve with FastAPI
FROM node:20-alpine AS angular-builder
WORKDIR /app
COPY client/package*.json ./
RUN npm ci
COPY client/ ./
RUN npm run build -- --configuration production

# Final image
FROM python:3.12-slim

# Create app directory
WORKDIR /app

# Copy and install Python deps
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server/ .

# Copy built Angular app from previous stage
COPY --from=angular-builder /app/dist/client/browser ./static

# Expose port (Render uses $PORT, fallback to 8000)
EXPOSE 8000

# Use $PORT if set (Render), otherwise 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]