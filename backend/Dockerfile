# Use an official Python runtime as a parent image
FROM python:3.13

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc git g++ curl gnupg2

# Upgrade pip
RUN python -m pip install --upgrade pip

# Copy requirements.txt before installing dependencies
COPY ./requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt


# Copy the current directory contents into the container
COPY . /app

# Argument for private registry
ARG PAT
ENV PAT=$PAT
RUN pip3 install "recall-space-agents[all]==4.1.15" --index-url "https://RecallSpace:${PAT}@pkgs.dev.azure.com/RecallSpace/recall-space-developments/_packaging/recall-space-agents/pypi/simple/"

# Expose port 8000 for FastAPI
EXPOSE 8000

# Run Alembic migrations and start the application
CMD ["bash", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
