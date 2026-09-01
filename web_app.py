import threading
import time

import cv2
from flask import Flask, jsonify, render_template, request, Response

from main import PeopleOccupancySystem


app = Flask(__name__)
system = PeopleOccupancySystem()
frame_lock = threading.Lock()
started = False


def ensure_started():
    global started
    if not started:
        with frame_lock:
            if not started:
                system.initialize_camera()
                system.initialize_components()
                started = True


def read_processed_frame():
    ensure_started()
    with frame_lock:
        ok, frame = system.cap.read()
        if not ok:
            return None
        system.frame_count += 1
        system.update_fps()
        return system.process_frame(frame)


def camera_stream():
    while True:
        frame = read_processed_frame()
        if frame is None:
            time.sleep(0.25)
            continue

        ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 82])
        if ok:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + encoded.tobytes() + b"\r\n"
            )


def get_status():
    if system.counter is None:
        return {
            "occupancy": 0,
            "entries": 0,
            "exits": 0,
            "sound_enabled": system.sound_enabled,
            "fps": 0,
            "last_event": None,
            "last_event_time": None,
        }

    return {
        "occupancy": system.counter.get_current_occupancy(),
        "entries": system.counter.get_total_entries(),
        "exits": system.counter.get_total_exits(),
        "sound_enabled": system.sound_enabled,
        "fps": round(system.current_fps, 1),
        "last_event": system.last_event,
        "last_event_time": system.last_event_time,
    }


@app.get("/")
def dashboard():
    return render_template("index.html")


@app.get("/video_feed")
def video_feed():
    return Response(
        camera_stream(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/api/status")
def status():
    return jsonify(get_status())


@app.post("/api/reset")
def reset():
    ensure_started()
    with frame_lock:
        system.counter.reset()
        system.last_event = None
        system.last_event_time = None
    return jsonify(get_status())


@app.post("/api/sound")
def toggle_sound():
    payload = request.get_json(silent=True) or {}
    system.sound_enabled = payload.get("enabled", True)
    return jsonify(get_status())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)
