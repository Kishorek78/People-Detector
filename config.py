# Camera
CAMERA_INDEX = 0

# YOLO model
MODEL_NAME = "yolov8n.pt"

# Detection confidence
CONFIDENCE = 0.50

# People class in COCO dataset
PERSON_CLASS_ID = 0

# Line position as percentage of frame height
LINE_POSITION = 0.50

# Audio - disable on cloud deployment (no audio devices)
import os
ENABLE_SOUND = os.getenv("ENABLE_SOUND", "false").lower() == "true"

# Maximum occupancy allowed for tone mapping
MAX_TONE_COUNT = 10

# Camera mode: "webcam" or "rtsp"
# For cloud deployment, use "rtsp" and set RTSP_URL environment variable
CAMERA_MODE = os.getenv("CAMERA_MODE", "rtsp")

# Example: "rtsp://username:password@192.168.1.100:554/stream"
# For Railway: Set this in Railway Variables tab
RTSP_URL = os.getenv("RTSP_URL", "rtsp://username:password@192.168.1.100:554/stream")

# Display settings
DISPLAY_FPS = True
DISPLAY_CONFIDENCE = True