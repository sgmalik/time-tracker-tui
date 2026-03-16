"""Data models for the Time Tracker application"""


class TimeEntry:
    """Represents a single time tracking entry"""
    
    def __init__(self, id: str, date: str, task: str, project: str, 
                 duration_minutes: int, description: str = ""):
        self.id = id
        self.date = date  # YYYY-MM-DD
        self.task = task
        self.project = project
        self.duration_minutes = duration_minutes
        self.description = description

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'date': self.date,
            'task': self.task,
            'project': self.project,
            'duration_minutes': self.duration_minutes,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data):
        """Create TimeEntry from dictionary"""
        return cls(**data)
