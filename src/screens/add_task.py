"""Add Task Screen - for creating new time entries"""
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Label, Input, Button
from textual.binding import Binding
from textual.screen import Screen
from datetime import datetime
from ..data_store import DataStore
from ..models import TimeEntry


class AddTaskScreen(Screen):
    """Screen for adding a new task"""
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, data_store: DataStore, date: datetime, callback=None):
        super().__init__()
        self.data_store = data_store
        self.date = date
        self.callback = callback

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="add-task-container"):
            yield Label("[bold cyan]Add Task[/bold cyan]", id="form-title")
            yield Label("Task:")
            yield Input(placeholder="What did you work on?", id="task-input")
            yield Label("Project:")
            yield Input(placeholder="Which project?", id="project-input")
            yield Label("Description:")
            yield Input(placeholder="Additional details (optional)", id="description-input")
            yield Label("Hours:")
            yield Input(placeholder="0", id="hours-input")
            yield Label("Minutes:")
            yield Input(placeholder="0", id="minutes-input")
            with Horizontal():
                yield Button("Save", variant="success", id="save-button")
                yield Button("Cancel", variant="error", id="cancel-button")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-button":
            self.save_task()
        elif event.button.id == "cancel-button":
            if self.callback:
                self.callback(False)
            self.app.pop_screen()

    def action_cancel(self) -> None:
        """Handle escape key to cancel"""
        if self.callback:
            self.callback(False)
        self.app.pop_screen()

    def save_task(self):
        """Validate and save the new task"""
        task_input = self.query_one("#task-input", Input)
        project_input = self.query_one("#project-input", Input)
        description_input = self.query_one("#description-input", Input)
        hours_input = self.query_one("#hours-input", Input)
        minutes_input = self.query_one("#minutes-input", Input)
        
        task = task_input.value.strip()
        project = project_input.value.strip()
        description = description_input.value.strip()
        
        if not task or not project:
            self.notify("Task and Project are required!", severity="error")
            return
        
        try:
            hours = int(hours_input.value or "0")
            minutes = int(minutes_input.value or "0")
        except ValueError:
            self.notify("Invalid hours or minutes!", severity="error")
            return
        
        total_minutes = hours * 60 + minutes
        
        if total_minutes == 0:
            self.notify("Duration must be greater than 0!", severity="error")
            return
        
        entry = TimeEntry(
            id=f"{datetime.now().timestamp()}",
            date=self.date.strftime("%Y-%m-%d"),
            task=task,
            project=project,
            duration_minutes=total_minutes,
            description=description
        )
        
        self.data_store.add_entry(entry)
        self.notify(f"Added task: {task}", severity="information")
        if self.callback:
            self.callback(True)
        self.app.pop_screen()
