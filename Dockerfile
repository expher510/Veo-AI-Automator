# Use Python 3.10
FROM python:3.10-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and system dependencies
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy the rest of the code
COPY . .

# Expose port (HF Spaces uses 7860)
EXPOSE 7860

# Run the application
CMD ["python", "main.py"]
