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
            yield Label("Start Time (24hr HH:MM):")
            yield Input(placeholder="08:30", id="start-time-input")
            yield Label("End Time (24hr HH:MM):")
            yield Input(placeholder="09:00", id="end-time-input")
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
        start_time_input = self.query_one("#start-time-input", Input)
        end_time_input = self.query_one("#end-time-input", Input)
        
        task = task_input.value.strip()
        project = project_input.value.strip()
        description = description_input.value.strip()
        start_time = start_time_input.value.strip()
        end_time = end_time_input.value.strip()
        
        if not task or not project:
            self.notify("Task and Project are required!", severity="error")
            return
        
        if not start_time or not end_time:
            self.notify("Start and End times are required!", severity="error")
            return
        
        # Validate time format
        try:
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")
        except ValueError:
            self.notify("Invalid time format! Use 24hr HH:MM (e.g., 08:30)", severity="error")
            return
        
        # Validate end time is after start time
        start_dt = datetime.strptime(start_time, "%H:%M")
        end_dt = datetime.strptime(end_time, "%H:%M")
        if end_dt <= start_dt:
            self.notify("End time must be after start time!", severity="error")
            return
        
        entry = TimeEntry(
            id=f"{datetime.now().timestamp()}",
            date=self.date.strftime("%Y-%m-%d"),
            task=task,
            project=project,
            start_time=start_time,
            end_time=end_time,
            description=description
        )
        
        self.data_store.add_entry(entry)
        self.notify(f"Added task: {task}", severity="information")
        if self.callback:
            self.callback(True)
        self.app.pop_screen()
