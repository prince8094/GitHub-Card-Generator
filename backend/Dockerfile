# Use a slim Python image
FROM python:3.12-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml README.md uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen

# Copy source code
COPY . .

# Expose port 8080
EXPOSE 8080

# Command to run the application
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
