from ultralytics import YOLO


class PersonTracker:
  
    def __init__(self, model_name, confidence=0.5):
      
        self.model = YOLO(model_name)
        self.confidence = confidence

    def track(self, frame):
       
        results = self.model.track(
            frame,
            persist=True,
            classes=[0],  
            conf=self.confidence,
            verbose=False
        )

        return results[0]