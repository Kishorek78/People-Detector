FROM python:3.11-slim

# Install all required system dependencies for OpenCV and multimedia
RUN apt-get update && apt-get install -y \
    # X11 and graphics libraries
    libxcb1 \
    libx11-6 \
    libxext6 \
    libxrender-dev \
    # Core dependencies
    libglib2.0-0 \
    libsm6 \
    libgomp1 \
    # Video codec support
    libavcodec59 \
    libavformat59 \
    libswscale6 \
    # Additional libraries
    libopenblas0 \
    libjasper1 \
    libtiff6 \
    libjasper-runtime \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose port 8080 (Railway default)
EXPOSE 8080

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "web_app:app"]
