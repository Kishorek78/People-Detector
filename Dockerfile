FROM python:3.11-slim

# Install required system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libxcb1 \
    libx11-6 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "web_app:app"]
