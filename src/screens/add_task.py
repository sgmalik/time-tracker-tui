"""Add Task Screen - for creating new time entries"""
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Label, Input, Button, Select
from textual.binding import Binding
from textual.screen import Screen
from datetime import datetime
from ..data_store import DataStore
from ..models import TimeEntry

# Standard project list
STANDARD_PROJECTS = [
    "General AI",
    "BMS-POC",
    "SPD-DTM POC",
    "SPD-MDR-POC",
    "SCE-POC",
    "DEV-MEETING",
    "ADMIN",
    "[+ Add New Project]"
]


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
        # Get all existing projects from data store
        all_projects = set()
        for entries in self.data_store.entries.values():
            for entry in entries:
                all_projects.add(entry.project)
        
        # Combine standard projects with any custom ones
        project_options = list(set(STANDARD_PROJECTS + list(all_projects)))
        project_options.sort()
        # Make sure "[+ Add New Project]" is last
        if "[+ Add New Project]" in project_options:
            project_options.remove("[+ Add New Project]")
        project_options.append("[+ Add New Project]")
        
        yield Header()
        with Container(id="add-task-container"):
            yield Label("[bold cyan]Add Task[/bold cyan]", id="form-title")
            yield Label("Task:")
            yield Input(placeholder="What did you work on?", id="task-input")
            yield Label("Project:")
            yield Select([(proj, proj) for proj in project_options], id="project-select", allow_blank=False, value=project_options[0])
            yield Input(placeholder="Custom project name", id="custom-project-input", classes="hidden")
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

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle project selection changes"""
        if event.select.id == "project-select":
            custom_input = self.query_one("#custom-project-input", Input)
            if event.value == "[+ Add New Project]":
                custom_input.remove_class("hidden")
                custom_input.focus()
            else:
                custom_input.add_class("hidden")
                custom_input.value = ""

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
        project_select = self.query_one("#project-select", Select)
        custom_project_input = self.query_one("#custom-project-input", Input)
        description_input = self.query_one("#description-input", Input)
        start_time_input = self.query_one("#start-time-input", Input)
        end_time_input = self.query_one("#end-time-input", Input)
        
        task = task_input.value.strip()
        
        # Get project from either select or custom input
        if project_select.value == "[+ Add New Project]":
            project = custom_project_input.value.strip()
            if not project:
                self.notify("Please enter a custom project name!", severity="error")
                return
        else:
            project = project_select.value
        
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
