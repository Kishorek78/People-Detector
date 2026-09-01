
class PeopleCounter:
  
    def __init__(self):
        self.people_in_frame = set()
        
        self.people_ever_seen = set()
        
        self.total_entries = 0
        self.total_exits = 0
        
        self.initialized = False

    def update(self, current_track_ids):
        """Update visible IDs and return the people who entered or exited."""
        current_ids = set(current_track_ids)
        
        if not self.initialized:
            self.people_in_frame = current_ids.copy()
            self.people_ever_seen = current_ids.copy()
            self.initialized = True
            return {"entered": [], "exited": []}
        
        entered = current_ids - self.people_in_frame
        exited = self.people_in_frame - current_ids
        
        for track_id in entered:
            self.people_ever_seen.add(track_id)
            print(f"  Person entered: ID {track_id}")
        
        self.total_entries += len(entered)
        self.total_exits += len(exited)
        self.people_in_frame = current_ids.copy()
        
        return {"entered": sorted(entered), "exited": sorted(exited)}

    def reset(self):
        self.people_in_frame = set()
        self.people_ever_seen = set()
        self.total_entries = 0
        self.total_exits = 0
        self.initialized = False

    def get_current_occupancy(self):
        return len(self.people_in_frame)
    
    def get_total_entries(self):
        return self.total_entries

    def get_total_exits(self):
        return self.total_exits