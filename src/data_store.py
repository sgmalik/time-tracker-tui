"""Data storage and persistence for Time Tracker"""
import json
from pathlib import Path
from typing import List, Dict
from .models import TimeEntry


class DataStore:
    """Manages persistence and retrieval of time entries"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.data_file = self.data_dir / 'entries.json'
        self.entries: Dict[str, List[TimeEntry]] = {}
        self._load()

    def _load(self):
        """Load entries from JSON file"""
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize file with empty JSON object if it doesn't exist or is empty
        if not self.data_file.exists() or self.data_file.stat().st_size == 0:
            with open(self.data_file, 'w') as f:
                json.dump({}, f)
        
        with open(self.data_file, 'r') as f:
            data = json.load(f)
            for date, entries in data.items():
                self.entries[date] = [TimeEntry.from_dict(e) for e in entries]

    def _save(self):
        """Save entries to JSON file"""
        data = {}
        for date, entries in self.entries.items():
            data[date] = [e.to_dict() for e in entries]
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_entry(self, entry: TimeEntry):
        """Add a new time entry"""
        if entry.date not in self.entries:
            self.entries[entry.date] = []
        self.entries[entry.date].append(entry)
        self._save()

    def update_entry(self, entry_id: str, **updates):
        """Update an existing entry by ID"""
        for date, entries in self.entries.items():
            for entry in entries:
                if entry.id == entry_id:
                    for key, value in updates.items():
                        setattr(entry, key, value)
                    self._save()
                    return

    def delete_entry(self, entry_id: str):
        """Delete an entry by ID"""
        for date, entries in self.entries.items():
            self.entries[date] = [e for e in entries if e.id != entry_id]
        # Remove dates with no entries to keep the dictionary clean
        self.entries = {date: entries for date, entries in self.entries.items() if entries}
        self._save()

    def get_entries_for_date(self, date: str) -> List[TimeEntry]:
        """Get all entries for a specific date"""
        return self.entries.get(date, [])

    def get_entries_for_month(self, year: int, month: int) -> Dict[str, List[TimeEntry]]:
        """Get all entries for a specific month"""
        month_str = f"{year}-{month:02d}"
        return {date: entries for date, entries in self.entries.items() 
                if date.startswith(month_str)}

    def get_total_hours_for_month(self, year: int, month: int) -> float:
        """Calculate total hours tracked in a month"""
        entries = self.get_entries_for_month(year, month)
        total_minutes = sum(
            sum(e.duration_minutes for e in day_entries) 
            for day_entries in entries.values()
        )
        return total_minutes / 60.0
