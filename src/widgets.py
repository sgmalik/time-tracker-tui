"""Widget components for Time Tracker UI"""
from textual.widgets import Static
from textual.containers import ScrollableContainer
from datetime import datetime, timedelta
from typing import Optional
import calendar as cal
from .data_store import DataStore
from .models import TimeEntry


def military_to_12hour(time_str: str) -> str:
    """Convert military time (HH:MM) to 12-hour format (H:MM AM/PM)"""
    try:
        time_obj = datetime.strptime(time_str, "%H:%M")
        return time_obj.strftime("%-I:%M %p")  # %-I removes leading zero
    except:
        return time_str


class RecentTasksWidget(Static):
    """Widget showing the 5 most recent tasks"""
    
    def __init__(self, data_store: DataStore):
        super().__init__()
        self.data_store = data_store

    def render(self) -> str:
        # Get all entries with their date and start time
        all_entries = []
        for date in self.data_store.entries.keys():
            for entry in self.data_store.entries[date]:
                all_entries.append((date, entry))
        
        # Sort by date (descending) then by start_time (descending) - most recent first
        all_entries.sort(key=lambda x: (x[0], x[1].start_time), reverse=True)
        
        # Take the 5 most recent
        recent = all_entries[:5]
        
        lines = []
        lines.append("[bold cyan]━━━━━━━━━━━━━━━━━━━━━━ Recent Tasks ━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]")
        
        if not recent:
            lines.append("[dim]No tasks yet - press 'A' to add your first task[/dim]")
        else:
            for date_str, entry in recent:
                # Format date
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                date_display = date_obj.strftime("%b %d")
                
                # Format time display with duration
                if entry.end_time:
                    hours = entry.duration_minutes // 60
                    minutes = entry.duration_minutes % 60
                    duration_str = f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
                    start_12h = military_to_12hour(entry.start_time)
                    end_12h = military_to_12hour(entry.end_time)
                    time_display = f"{start_12h}-{end_12h} [cyan]({duration_str})[/cyan]"
                else:
                    start_12h = military_to_12hour(entry.start_time)
                    time_display = f"{start_12h}-... [yellow](in progress)[/yellow]"
                
                task_display = f"  {date_display} {time_display}: [bold]{entry.task}[/bold] [dim]({entry.project})[/dim]"
                lines.append(task_display)
        
        return "\n".join(lines)


class CalendarWidget(Static):
    """A calendar widget showing a month view"""
    
    def __init__(self, data_store: DataStore):
        super().__init__()
        self.data_store = data_store
        self.selected_date = datetime.now()
        self.today = datetime.now()
        # Set calendar to start on Sunday
        cal.setfirstweekday(cal.SUNDAY)

    def render(self) -> str:
        year = self.selected_date.year
        month = self.selected_date.month
        
        # Get month data
        month_entries = self.data_store.get_entries_for_month(year, month)
        total_hours = self.data_store.get_total_hours_for_month(year, month)
        
        # Build calendar with even larger cells to fill screen better
        cell_width = 20
        month_name = self.selected_date.strftime("%B %Y")
        lines = []
        lines.append(f"[bold cyan]{month_name}[/bold cyan]  (Total: {total_hours:.1f}h)")
        lines.append("")
        
        # Day headers
        lines.append("+" + ("-" * cell_width + "+") * 7)
        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        header = "|" + "|".join(f"{name:^{cell_width}}" for name in day_names) + "|"
        lines.append(f"[bold]{header}[/bold]")
        lines.append("+" + ("-" * cell_width + "+") * 7)
        
        # Calendar days
        month_cal = cal.monthcalendar(year, month)
        for week_idx, week in enumerate(month_cal):
            week_lines = ["", "", "", ""]  # 4 lines per week for more space
            
            for day in week:
                if day == 0:
                    # Empty cell
                    for i in range(4):
                        week_lines[i] += "|" + " " * cell_width
                else:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    has_entries = date_str in month_entries
                    
                    # Check if selected
                    is_selected = (day == self.selected_date.day and 
                                 month == self.selected_date.month and 
                                 year == self.selected_date.year)
                    
                    # Check if today
                    is_today = (day == self.today.day and 
                              month == self.today.month and 
                              year == self.today.year)
                    
                    # Line 0: empty space
                    week_lines[0] += "|" + " " * cell_width
                    
                    # Line 1: Format day number - center in cell_width
                    if is_selected:
                        day_str = f"[{day}]"
                        week_lines[1] += f"|[bold green]{day_str:^{cell_width}}[/bold green]"
                    elif is_today:
                        day_str = f"<{day}>"
                        week_lines[1] += f"|[bold red]{day_str:^{cell_width}}[/bold red]"
                    else:
                        week_lines[1] += f"|{day:^{cell_width}}"
                    
                    # Line 2: indicator
                    if has_entries:
                        week_lines[2] += f"|[cyan]{'*':^{cell_width}}[/cyan]"
                    else:
                        week_lines[2] += "|" + " " * cell_width
                    
                    # Line 3: empty space
                    week_lines[3] += "|" + " " * cell_width
            
            # Add closing borders
            for i in range(4):
                week_lines[i] += "|"
                lines.append(week_lines[i])
            
            # Add separator between weeks (but not after last week)
            if week_idx < len(month_cal) - 1:
                lines.append("+" + ("-" * cell_width + "+") * 7)
        
        # Bottom border
        lines.append("+" + ("-" * cell_width + "+") * 7)
        
        return "\n".join(lines)

    def move_day(self, delta: int):
        """Move selection by days"""
        self.selected_date += timedelta(days=delta)
        self.refresh()

    def move_week(self, delta: int):
        """Move selection by weeks"""
        self.selected_date += timedelta(weeks=delta)
        self.refresh()

    def move_month(self, delta: int):
        """Move selection by months"""
        month = self.selected_date.month + delta
        year = self.selected_date.year
        
        while month > 12:
            month -= 12
            year += 1
        while month < 1:
            month += 12
            year -= 1
        
        # Handle day overflow (e.g., Jan 31 -> Feb 31 doesn't exist)
        day = min(self.selected_date.day, cal.monthrange(year, month)[1])
        self.selected_date = datetime(year, month, day)
        self.refresh()

    def go_to_today(self):
        """Jump to today's date"""
        self.selected_date = datetime.now()
        self.refresh()


class TaskListWidget(ScrollableContainer):
    """Widget showing tasks for a specific day"""
    
    def __init__(self, data_store: DataStore):
        super().__init__()
        self.data_store = data_store
        self.date = datetime.now()
        self.selected_index = 0
        self.content_widget = Static()

    def compose(self):
        """Compose with static content inside"""
        yield self.content_widget

    def on_mount(self):
        """Initial render when mounted"""
        self.update_display()

    def set_date(self, date: datetime):
        """Set the date to display tasks for"""
        self.date = date
        self.selected_index = 0
        self.update_display()

    def update_display(self):
        """Update the content display"""
        date_str = self.date.strftime("%A, %B %d, %Y")
        entries = self.data_store.get_entries_for_date(self.date.strftime("%Y-%m-%d"))
        
        lines = []
        lines.append(f"[bold cyan]Tasks for {date_str}[/bold cyan]")
        lines.append("─" * 40)
        
        if not entries:
            lines.append("[dim]  No tasks[/dim]")
            lines.append("[dim]  Press 'A' to add[/dim]")
        else:
            total_minutes = sum(e.duration_minutes for e in entries)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            lines.append(f"[bold cyan]Total: {hours}h {minutes}m[/bold cyan]")
            lines.append("")
            
            for i, entry in enumerate(entries):
                prefix = "► " if i == self.selected_index else "  "
                
                hours = entry.duration_minutes // 60
                minutes = entry.duration_minutes % 60
                
                if i == self.selected_index:
                    task_line = f"{prefix}[bold green]{entry.task}[/bold green]"
                else:
                    task_line = f"{prefix}{entry.task}"
                
                lines.append(task_line)
                
                # Show start-end times and duration in 12-hour format
                if entry.end_time:
                    start_12h = military_to_12hour(entry.start_time)
                    end_12h = military_to_12hour(entry.end_time)
                    time_info = f"  {start_12h}-{end_12h}"
                    details = f"{time_info} ({hours}h {minutes}m)"
                else:
                    # In progress task
                    start_12h = military_to_12hour(entry.start_time)
                    time_info = f"  {start_12h}-..."
                    details = f"{time_info} [yellow](in progress)[/yellow]"
                if i == self.selected_index:
                    lines.append(f"[green]{details}[/green]")
                    lines.append(f"[green]  {entry.project}[/green]")
                else:
                    lines.append(f"[dim]{details}[/dim]")
                    lines.append(f"[dim]  {entry.project}[/dim]")
                
                if entry.description:
                    desc_text = f"  {entry.description[:35]}..."
                    if i == self.selected_index:
                        lines.append(f"[green]{desc_text}[/green]")
                    else:
                        lines.append(f"[dim]{desc_text}[/dim]")
                
                lines.append("")
        
        self.content_widget.update("\n".join(lines))
        
        # Auto-scroll to selected item
        if entries and self.selected_index < len(entries):
            # Calculate approximate line position
            header_lines = 4
            lines_per_entry = 5
            target_line = header_lines + (self.selected_index * lines_per_entry)
            self.scroll_to(y=target_line, animate=True)

    def move_selection(self, delta: int):
        """Move task selection up or down"""
        entries = self.data_store.get_entries_for_date(self.date.strftime("%Y-%m-%d"))
        if entries:
            self.selected_index = max(0, min(len(entries) - 1, self.selected_index + delta))
            self.update_display()

    def get_selected_entry(self) -> Optional[TimeEntry]:
        """Get the currently selected entry"""
        entries = self.data_store.get_entries_for_date(self.date.strftime("%Y-%m-%d"))
        if 0 <= self.selected_index < len(entries):
            return entries[self.selected_index]
        return None
