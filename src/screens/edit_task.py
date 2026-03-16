"""Edit Task Screen - for modifying existing time entries"""
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Label, Input, Button
from textual.binding import Binding
from textual.screen import Screen
from datetime import datetime
from ..data_store import DataStore
from ..models import TimeEntry


class EditTaskScreen(Screen):
    """Screen for editing an existing task"""
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, data_store: DataStore, entry: TimeEntry, callback=None):
        super().__init__()
        self.data_store = data_store
        self.entry = entry
        self.callback = callback

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="add-task-container"):
            yield Label("[bold cyan]Edit Task[/bold cyan]", id="form-title")
            yield Label("Task:")
            yield Input(value=self.entry.task, placeholder="What did you work on?", id="task-input")
            yield Label("Project:")
            yield Input(value=self.entry.project, placeholder="Which project?", id="project-input")
            yield Label("Description:")
            yield Input(value=self.entry.description, placeholder="Additional details (optional)", id="description-input")
            yield Label("Hours:")
            yield Input(value=str(self.entry.duration_minutes // 60), placeholder="0", id="hours-input")
            yield Label("Minutes:")
            yield Input(value=str(self.entry.duration_minutes % 60), placeholder="0", id="minutes-input")
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
        """Validate and update the existing task"""
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
        
        # Update the existing entry
        self.data_store.update_entry(
            self.entry.id,
            task=task,
            project=project,
            description=description,
            duration_minutes=total_minutes
        )
        
        self.notify(f"Updated task: {task}", severity="information")
        if self.callback:
            self.callback(True)
        self.app.pop_screen()
