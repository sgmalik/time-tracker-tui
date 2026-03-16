"""Time Tracker - A TUI application for tracking time spent on tasks"""
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Horizontal
from textual.binding import Binding

from src.data_store import DataStore
from src.widgets import RecentTasksWidget, CalendarWidget, TaskListWidget
from src.screens import AddTaskScreen, EditTaskScreen


class TimeTrackerApp(App):
    """Time tracking TUI application"""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    
    RecentTasksWidget {
        width: 100%;
        height: 7;
        min-height: 7;
        margin-bottom: 1;
        content-align: center middle;
        text-align: center;
        background: $surface;
        border: solid $primary;
        padding: 0 1;
    }
    
    #main-container {
        width: 100%;
        height: 1fr;
        padding: 0;
    }
    
    TaskListWidget {
        width: 25%;
        height: 1fr;
        margin-right: 3;
        border: solid $primary;
        padding: 1;
    }
    
    CalendarWidget {
        width: 75%;
        height: auto;
        padding: 0;
    }
    
    #add-task-container {
        padding: 1 2;
        height: auto;
    }
    
    #form-title {
        margin-bottom: 1;
    }
    
    Label {
        margin-top: 1;
    }
    
    Input {
        margin-bottom: 1;
    }
    
    Button {
        margin-top: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("a", "add_task", "Add Task"),
        Binding("e", "edit_task", "Edit Task"),
        Binding("d", "delete_task", "Delete"),
        Binding("t", "go_to_today", "Today"),
        Binding("h", "prev_day", "← Day", show=False),
        Binding("l", "next_day", "→ Day", show=False),
        Binding("left", "prev_day", "← Day"),
        Binding("right", "next_day", "→ Day"),
        Binding("k", "prev_week", "↑ Week", show=False),
        Binding("j", "next_week", "↓ Week", show=False),
        Binding("up", "prev_week", "↑ Week"),
        Binding("down", "next_week", "↓ Week"),
        Binding("w", "task_up", "Task ↑", show=False),
        Binding("x", "task_down", "Task ↓", show=False),
    ]
    
    def __init__(self):
        super().__init__()
        self.data_store = DataStore()
        self.recent_tasks_widget = None
        self.calendar_widget = None
        self.task_list_widget = None

    def compose(self) -> ComposeResult:
        yield Header()
        self.recent_tasks_widget = RecentTasksWidget(self.data_store)
        yield self.recent_tasks_widget
        
        with Horizontal(id="main-container"):
            self.task_list_widget = TaskListWidget(self.data_store)
            self.calendar_widget = CalendarWidget(self.data_store)
            yield self.task_list_widget
            yield self.calendar_widget
        
        yield Footer()

    def refresh_all_widgets(self):
        """Force refresh all widgets with latest data"""
        # Update task list to match selected date
        if self.task_list_widget and self.calendar_widget:
            self.task_list_widget.date = self.calendar_widget.selected_date
            self.task_list_widget.update_display()
        
        # Force refresh all widgets with full re-render
        if self.recent_tasks_widget:
            self.recent_tasks_widget.refresh()
        if self.calendar_widget:
            self.calendar_widget.refresh()

    def action_add_task(self):
        """Open the add task screen with callback"""
        def on_add_complete(saved: bool):
            if saved:
                self.refresh_all_widgets()
        
        self.push_screen(
            AddTaskScreen(self.data_store, self.calendar_widget.selected_date, on_add_complete)
        )

    def action_edit_task(self):
        """Open the edit task screen with callback"""
        entry = self.task_list_widget.get_selected_entry()
        if entry:
            def on_edit_complete(saved: bool):
                if saved:
                    self.refresh_all_widgets()
            
            self.push_screen(EditTaskScreen(self.data_store, entry, on_edit_complete))
        else:
            self.notify("No task selected to edit", severity="warning")

    def action_delete_task(self):
        """Delete the currently selected task"""
        entry = self.task_list_widget.get_selected_entry()
        if entry:
            self.data_store.delete_entry(entry.id)
            self.refresh_all_widgets()
            self.notify(f"Deleted task: {entry.task}", severity="information")

    def action_prev_day(self):
        """Navigate to previous day"""
        self.calendar_widget.move_day(-1)
        self.task_list_widget.set_date(self.calendar_widget.selected_date)

    def action_next_day(self):
        """Navigate to next day"""
        self.calendar_widget.move_day(1)
        self.task_list_widget.set_date(self.calendar_widget.selected_date)

    def action_prev_week(self):
        """Navigate to previous week"""
        self.calendar_widget.move_week(-1)
        self.task_list_widget.set_date(self.calendar_widget.selected_date)

    def action_next_week(self):
        """Navigate to next week"""
        self.calendar_widget.move_week(1)
        self.task_list_widget.set_date(self.calendar_widget.selected_date)

    def action_prev_month(self):
        """Navigate to previous month"""
        self.calendar_widget.move_month(-1)
        self.task_list_widget.set_date(self.calendar_widget.selected_date)

    def action_next_month(self):
        """Navigate to next month"""
        self.calendar_widget.move_month(1)
        self.task_list_widget.set_date(self.calendar_widget.selected_date)

    def action_go_to_today(self):
        """Jump to today's date"""
        self.calendar_widget.go_to_today()
        self.task_list_widget.set_date(self.calendar_widget.selected_date)

    def action_task_up(self):
        """Move task selection up"""
        self.task_list_widget.move_selection(-1)

    def action_task_down(self):
        """Move task selection down"""
        self.task_list_widget.move_selection(1)

    def on_key(self, event):
        """Handle additional key presses"""
        if event.character == "<" or event.character == ",":
            self.action_prev_month()
        elif event.character == ">" or event.character == ".":
            self.action_next_month()


def main():
    """Main entry point"""
    app = TimeTrackerApp()
    app.run()


if __name__ == "__main__":
    main()
