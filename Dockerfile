FROM python:3.11-slim

# Install system dependencies (for PostgreSQL, OpenCV, and Selenium)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    gnupg \
    curl \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libfontconfig1 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome for Selenium job scraping
RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy the rest of the application code
COPY . .

# Hugging Face Spaces requires exposing port 7860
EXPOSE 7860

# Create a non-root user (Hugging Face Spaces requirement for security)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Command to run the application using Gunicorn
# app:create_app() tells gunicorn to call the factory function in app.py
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:create_app()", "--timeout", "120", "--workers", "2"]
