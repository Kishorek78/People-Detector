import cv2
import sys
from datetime import datetime

from config import (
    CAMERA_INDEX,
    MODEL_NAME,
    CONFIDENCE,
    LINE_POSITION,
    ENABLE_SOUND,
    CAMERA_MODE,
    RTSP_URL,
    DISPLAY_FPS,
    DISPLAY_CONFIDENCE
)

from detector.tracker import PersonTracker
from audio.tones import TonePlayer
from utils.counter import PeopleCounter


class PeopleOccupancySystem:
 
    def __init__(self):
        self.cap = None
        self.tracker = None
        self.tone_player = None
        self.counter = None
        self.frame_count = 0
        self.fps_timer = 0
        self.current_fps = 0
        self.sound_enabled = ENABLE_SOUND

        # Performance monitoring
        self.total_entries = 0
        self.last_event = None
        self.last_event_time = None

    def initialize_camera(self):
        """Open camera (webcam or RTSP)."""
        if CAMERA_MODE == "webcam":
            self.cap = cv2.VideoCapture(CAMERA_INDEX)
            print(f"📷 Opened webcam (index {CAMERA_INDEX})")

        elif CAMERA_MODE == "rtsp":
            self.cap = cv2.VideoCapture(RTSP_URL)
            print(f"📷 Opened RTSP stream: {RTSP_URL}")

        else:
            raise ValueError(f"Invalid CAMERA_MODE: {CAMERA_MODE}")

        if not self.cap.isOpened():
            raise RuntimeError("❌ Could not open camera")

        # Optional: Set camera properties
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce latency

    def initialize_components(self):
        """Initialize YOLO tracker, tone player, and counter."""
        self.tracker = PersonTracker(MODEL_NAME, CONFIDENCE)
        print(f"🤖 Loaded YOLO model: {MODEL_NAME}")
        
        self.counter = PeopleCounter()
        print("📊 Counter initialized (tracks frame entries)")

        if ENABLE_SOUND:
            self.tone_player = TonePlayer()
            print("🔊 Tone player initialized")

    def print_banner(self):
        """Print startup banner."""
        print("\n" + "="*50)
        print("  People Detector - Frame Entry Counter")
        print("="*50)
        print(f"Camera mode: {CAMERA_MODE}")
        print(f"YOLO model: {MODEL_NAME}")
        print(f"Confidence: {CONFIDENCE}")
        print(f"Sound: {'ON' if self.sound_enabled else 'OFF'}")
        print("="*50)
        print("\nControls:")
        print("  Q - Quit")
        print("  R - Reset counter")
        print("  S - Toggle sound")
        print("\nNote: Counts only NEW people entering the frame")
        print("="*50 + "\n")

    def process_frame(self, frame):
        """
        Process a single video frame.

        Args:
            frame: OpenCV BGR image

        Returns:
            Annotated frame
        """
        height, width = frame.shape[:2]

      
        result = self.tracker.track(frame)


        current_track_ids = []
        
        if result.boxes is not None:
            for box in result.boxes:
                if box.id is not None:
                    current_track_ids.append(int(box.id[0]))

        events = self.counter.update(current_track_ids)
        current_occupancy = self.counter.get_current_occupancy()

        if events["entered"]:
            self.last_event = {"type": "entry", "count": len(events["entered"])}
            self.last_event_time = datetime.now().isoformat(timespec="seconds")
            if self.sound_enabled and self.tone_player is not None:
                self.tone_player.play_entry_tone(current_occupancy)
            print(f"ENTRY | {len(events['entered'])} person(s) | Current in frame: {current_occupancy}")

        if events["exited"]:
            self.last_event = {"type": "exit", "count": len(events["exited"])}
            self.last_event_time = datetime.now().isoformat(timespec="seconds")
            if self.sound_enabled and self.tone_player is not None:
                self.tone_player.play_exit_tone(len(events["exited"]))
            print(f"EXIT | {len(events['exited'])} person(s) | Current in frame: {current_occupancy}")

        if result.boxes is not None:

            boxes = result.boxes

            for box in boxes:

                # Get tracking ID
                if box.id is None:
                    continue

                track_id = int(box.id[0])

                # Get bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Calculate center
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                # Get confidence
                conf = float(box.conf[0]) if DISPLAY_CONFIDENCE else 0

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                # ID label
                label = f"ID: {track_id}"
                if DISPLAY_CONFIDENCE:
                    label += f" ({conf:.2f})"

                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

                # Center point
                cv2.circle(
                    frame,
                    (center_x, center_y),
                    5,
                    (0, 0, 255),
                    -1
                )

        # ==================================================
        # Display statistics
        # ==================================================
        
        current_count = self.counter.get_current_occupancy()
        total_entries = self.counter.get_total_entries()

        # Background box for stats
        cv2.rectangle(
            frame,
            (10, 10),
            (450, 90),
            (0, 0, 0),
            -1
        )

        # Current occupancy
        occupancy_text = f"People in frame: {current_count}"
        cv2.putText(
            frame,
            occupancy_text,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )
        
        # Total entries
        entries_text = f"Total entries: {total_entries}"
        cv2.putText(
            frame,
            entries_text,
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (100, 255, 255),
            2
        )

        # ==================================================
        # Display FPS
        # ==================================================

        if DISPLAY_FPS:
            fps_text = f"FPS: {self.current_fps:.1f}"
            cv2.putText(
                frame,
                fps_text,
                (width - 200, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (200, 200, 200),
                2
            )

        # ==================================================
        # Display sound status
        # ==================================================
        
        sound_status = "🔊 SOUND ON" if self.sound_enabled else "🔇 SOUND OFF"
        cv2.putText(
            frame,
            sound_status,
            (10, height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (100, 255, 100) if self.sound_enabled else (100, 100, 255),
            2
        )

        return frame

    def handle_input(self, key):
       
        if key == ord('q') or key == ord('Q'):
            print("\n👋 Quitting...")
            return False

        elif key == ord('r') or key == ord('R'):
            print("🔄 Resetting counter...")
            self.counter.reset()
            self.total_entries = 0

        elif key == ord('s') or key == ord('S'):
            self.sound_enabled = not self.sound_enabled
            status = "ON" if self.sound_enabled else "OFF"
            print(f"🔊 Sound turned {status}")

        return True

    def update_fps(self):
        """Update FPS counter."""
        if self.frame_count % 10 == 0:
            import time
            current_time = time.time()
            if hasattr(self, 'last_time'):
                elapsed = current_time - self.last_time
                self.current_fps = 10.0 / elapsed
            self.last_time = current_time

    def run(self):
        """Main application loop."""
        try:
            self.initialize_camera()
            self.initialize_components()
            self.print_banner()

            while True:

                ret, frame = self.cap.read()

                if not ret:
                    print("❌ Could not read frame")
                    break

                # Process frame
                frame = self.process_frame(frame)

                # Update FPS
                self.frame_count += 1
                self.update_fps()

                # Display
                cv2.imshow(
                    "People Occupancy Prototype",
                    frame
                )

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key != 255:  # Key pressed
                    if not self.handle_input(key):
                        break

        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()

        print("\n" + "="*50)
        print("  Shutdown Summary")
        print("="*50)
        print(f"Total frames processed: {self.frame_count}")
        print(f"Total people entries: {self.total_entries}")
        print(f"People in frame at end: {self.counter.get_current_occupancy()}")
        print("="*50 + "\n")


def main():
    """Entry point."""
    system = PeopleOccupancySystem()
    system.run()


if __name__ == "__main__":
    main()