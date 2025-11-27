
import random
import constants as C

class EventSystem:
    """Manages random disaster events"""
    def __init__(self, villages):
        self.villages = villages
        self.event_history = []
    
    def check_and_spawn_events(self, year, month):
        """Check if events should spawn this month"""
        # Random chance for event
        if random.random() < C.EVENT_BASE_CHANCE:
            self.spawn_random_event(year, month)
    
    def spawn_random_event(self, year, month):
        """Spawn a random disaster event"""
        # Choose random event type
        event_type = random.choice(list(C.EVENT_TYPES.keys()))
        
        alive_villages = [v for v in self.villages if v.is_alive and not v.is_capital]
        
        if not alive_villages:
            return
        
        num_affected = random.randint(1, min(3, len(alive_villages)))
        affected_villages = random.sample(alive_villages, num_affected)
        
        for village in affected_villages:
            village.add_event(event_type)
        
        village_names = [v.name for v in affected_villages]
        self.event_history.append((year, month, event_type, village_names))
        
        return event_type, village_names