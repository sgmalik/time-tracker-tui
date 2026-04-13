"""Data models for the Time Tracker application"""

from datetime import datetime


class TimeEntry:
    """Represents a single time tracking entry"""

    def __init__(
        self,
        id: str,
        date: str,
        task: str,
        project: str,
        start_time: str,
        end_time: str,
        description: str = "",
    ):
        self.id = id
        self.date = date  # YYYY-MM-DD
        self.task = task
        self.project = project
        self.start_time = start_time  # HH:MM format (e.g., "09:30")
        self.end_time = end_time  # HH:MM format (e.g., "10:00")
        self.description = description

    @property
    def duration_minutes(self) -> int:
        """Calculate duration in minutes from start and end times"""
        if not self.end_time:
            # Task is in progress, return 0 or calculate from start to now
            return 0
        try:
            start = datetime.strptime(self.start_time, "%H:%M")
            end = datetime.strptime(self.end_time, "%H:%M")
            delta = end - start
            return int(delta.total_seconds() / 60)
        except:
            return 0

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "date": self.date,
            "task": self.task,
            "project": self.project,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data):
        """Create TimeEntry from dictionary"""
        return cls(**data)
