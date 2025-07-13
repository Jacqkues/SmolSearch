FROM python:3.12-slim

RUN apt-get update && apt-get install -y git

ENV GROQ_API=


# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "/app/backend/main.py", "--port", "80", "--host", "0.0.0.0"]