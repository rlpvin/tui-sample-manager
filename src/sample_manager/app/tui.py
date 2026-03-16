import os
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, DataTable
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.screen import Screen
from textual import on

from sample_manager.app.controller import ApplicationController
from sample_manager.db.sample_repository import get_all_samples, search_samples, get_sample_by_id
from sample_manager.utils.playback import Player

class HelpScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Sample Manager Help", id="help_title"),
            Static(
                "Keyboard Shortcuts:\n\n"
                "q           - Quit Application\n"
                "s           - Refresh samples (maintains filters)\n"
                "f           - Focus Command / Search Modal\n"
                "l           - Toggle Full-Screen List View\n"
                "h           - Toggle this help screen\n"
                "c           - Clear results panel output\n\n"
                "List Shortcuts (when list focused):\n"
                "Arrows      - Navigate samples\n"
                "Space       - Play / Stop focused sample\n"
                "t           - Add Tag to selected sample\n"
                "r           - Add Rating to selected sample\n"
                "/           - Quick search dialog\n\n"
                "Commands (enter in Command Modal 'f'):\n\n"
                "scan              - Scan for new samples\n"
                "search <text>     - Search samples by name\n"
                "tag <id> <tag>    - Add tag to a sample\n"
                "untag <id> <tag>  - Remove tag from a sample\n"
                "bulk-tag <q> <t>  - Tag all results matching <q>\n"
                "tags              - List all available tags\n"
                "rate <id> <1-5>   - Rate a sample\n"
                "unrate <id>       - Remove rating from a sample\n"
                "stats             - Show database statistics\n\n"
                "Advanced Filtering (works in Search or Command Modal):\n\n"
                "tag:<name>        - Filter by tag\n"
                "type:<ext>        - Filter by file extension\n"
                "rating:<[><=]val> - Filter by rating (e.g., rating:>3)\n"
                "sort:<field>      - Sort (filename, rating, bpm, date)\n"
                "                    Use '-' for descending (e.g., sort:-bpm)\n"
                "Example: tag:kick type:wav rating:>3 search heavy\n",
                id="help_text"
            ),
            Static("Press any key to close", id="help_footer"),
            id="help_container"
        )

    def on_mount(self) -> None:
        self.styles.background = "rgba(0,0,0,0.8)"

    def on_key(self) -> None:
        self.app.pop_screen()

class InputDialog(ModalScreen):
    """A modal dialog to get text input."""
    
    def __init__(self, title: str, placeholder: str = "", callback=None):
        super().__init__()
        self.title_text = title
        self.placeholder = placeholder
        self.callback = callback

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.title_text, id="dialog_title"),
            Input(placeholder=self.placeholder, id="dialog_input"),
            Static("Press Enter to submit, Escape to cancel", id="dialog_footer"),
            id="dialog_container"
        )

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    @on(Input.Submitted)
    def handle_submit(self, event: Input.Submitted) -> None:
        if self.callback:
            self.callback(event.value)
        self.app.pop_screen()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()

class SampleTable(DataTable):
    """A specialized DataTable for samples with extra shortcuts."""
    
    BINDINGS = [
        Binding("t", "add_tag", "Add Tag", show=False),
        Binding("r", "add_rating", "Add Rating", show=False),
        Binding("/", "search", "Search", show=False),
        Binding("space", "toggle_playback", "Play", show=False),
    ]

    def action_toggle_playback(self) -> None:
        row_key = self.cursor_row
        if row_key is not None:
            # Get ID from first column
            row_data = self.get_row_at(row_key)
            sample_id = row_data[0]
            self.app.action_toggle_playback(sample_id)

    @on(DataTable.RowHighlighted)
    def on_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Stop playback when moving to a new sample, or auto-play if in audition mode."""
        if hasattr(self.app, "player"):
            self.app.player.stop()
            if getattr(self.app, "audition_mode", False):
                # Get ID from first column of the new row
                row_data = self.get_row_at(event.cursor_row)
                sample_id = row_data[0]
                self.app.action_toggle_playback(sample_id, is_auto=True)

    def action_search(self) -> None:
        self.app.prompt_search()

    def action_add_tag(self) -> None:
        row_key = self.cursor_row
        if row_key is not None:
            # Get ID from first column
            row_data = self.get_row_at(row_key)
            sample_id = row_data[0]
            self.app.prompt_tag(sample_id)

    def action_add_rating(self) -> None:
        row_key = self.cursor_row
        if row_key is not None:
            # Get ID from first column
            row_data = self.get_row_at(row_key)
            sample_id = row_data[0]
            self.app.prompt_rating(sample_id)

class SampleListScreen(Screen):
    """A full-screen view of the sample list."""
    
    BINDINGS = [
        Binding("l", "app.pop_screen", "Back to Dashboard"),
        Binding("escape", "app.pop_screen", "Back to Dashboard"),
        Binding("s", "refresh_samples", "Refresh"),
        Binding("f", "show_command_bar", "Command"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield SampleTable(id="full_sample_list")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(SampleTable)
        table.add_columns("ID", "Filename", "Tags", "Rating", "BPM", "Date")
        table.cursor_type = "row"
        table.focus()
        self.app.action_refresh_samples()

    def action_refresh_samples(self) -> None:
        self.app.action_refresh_samples()

    def action_show_command_bar(self) -> None:
        self.app.action_show_command_bar()

class CommandScreen(ModalScreen):
    """A modal screen for entering commands at the top."""

    def compose(self) -> ComposeResult:
        with Vertical(id="command_dialog_container"):
            yield Static("Enter Command / Search:", id="command_title")
            yield Input(placeholder="e.g., search kick, scan, tag 1 drum...", id="command_input")
            yield Static("Press Enter to run, Escape to cancel", id="command_footer")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    @on(Input.Submitted)
    def handle_submit(self, event: Input.Submitted) -> None:
        self.app.handle_command_text(event.value)
        self.app.pop_screen()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()

class SampleManagerApp(App):
    CSS = """
    Screen {
        background: #1a1b26;
        color: #c0caf5;
    }

    #main_container {
        height: 100%;
        width: 100%;
    }

    SampleTable {
        height: 1fr;
        border: solid #414868;
        background: #1a1b26;
    }

    SampleTable > .datatable--header {
        background: #24283b;
        color: #7aa2f7;
        text-style: bold;
    }

    SampleTable > .datatable--cursor {
        background: #364a82;
    }

    #input_area {
        height: auto;
        border: solid #414868;
        padding: 0 1;
        background: #24283b;
    }

    Input {
        background: #1a1b26;
        border: none;
        color: #c0caf5;
    }

    Input:focus {
        border: none;
    }

    #results_panel {
        height: 8;
        border: solid #414868;
        padding: 0 1;
        background: #24283b;
        color: #9ece6a;
        overflow-y: scroll;
    }

    #help_container {
        align: center middle;
        width: 60;
        height: 35;
        border: double #7aa2f7;
        background: #1a1b26;
        padding: 1 2;
    }

    #help_title {
        text-align: center;
        text-style: bold;
        color: #7aa2f7;
        margin-bottom: 1;
    }

    #help_footer {
        text-align: center;
        color: #565f89;
        margin-top: 1;
    }

    #dialog_container {
        align: center middle;
        width: 50;
        height: auto;
        border: double #7aa2f7;
        background: #1a1b26;
        padding: 1 2;
        margin: 2;
    }

    #dialog_title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #dialog_footer {
        text-align: center;
        color: #565f89;
        margin-top: 1;
    }

    #command_dialog_container {
        dock: top;
        width: 100%;
        height: auto;
        background: #24283b;
        border-bottom: solid #7aa2f7;
        padding: 0 1;
    }

    #command_title {
        text-style: bold;
        color: #7aa2f7;
    }

    #command_input {
        background: #1a1b26;
        border: none;
        color: #c0caf5;
    }

    #command_footer {
        color: #565f89;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("s", "refresh_samples", "Refresh"),
        Binding("f", "show_command_bar", "Command"),
        Binding("l", "show_list", "Full List"),
        Binding("h", "show_help", "Help"),
        Binding("c", "clear_results", "Clear Output"),
    ]

    def __init__(self):
        super().__init__()
        self.controller = ApplicationController()
        self.last_query = ""
        self.player = Player()
        self.audition_mode = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main_container"):
            yield SampleTable(id="sample_list")
            with Vertical(id="results_panel"):
                yield Static("System Output:", id="output_header")
                yield Static("", id="output_text")
        yield Footer()

    def on_unmount(self) -> None:
        """Ensure playback stops when application exits."""
        self.player.stop()

    def on_mount(self) -> None:
        table = self.query_one("#sample_list", SampleTable)
        table.add_columns("ID", "Filename", "Tags", "Rating", "BPM", "Date")
        table.cursor_type = "row"
        self.action_refresh_samples()

    def action_refresh_samples(self) -> None:
        """Fetch samples based on last query and update the active table."""
        self.perform_search(self.last_query)

    def action_focus_input(self) -> None:
        self.query_one(Input).focus()

    def action_show_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_show_list(self) -> None:
        self.push_screen(SampleListScreen())

    def action_clear_results(self) -> None:
        self.query_one("#output_text", Static).update("")
        self._log_history = []

    def log_result(self, message: str) -> None:
        """Update the results panel with a message."""
        try:
            output = self.query_one("#output_text", Static)
        except:
            return
            
        if not hasattr(self, "_log_history"):
            self._log_history = []
        self._log_history.append(f"> {message}")
        # Keep only the last 50 messages
        self._log_history = self._log_history[-50:]
        output.update("\n".join(self._log_history))
        # Auto-scroll the container to the bottom
        output.parent.scroll_end(animate=False)

    def prompt_tag(self, sample_id: str) -> None:
        def handle_tag(tag_name: str):
            if tag_name.strip():
                result = self.controller.handle_input(f"tag {sample_id} {tag_name}")
                self.log_result(result)
                self.action_refresh_samples()
        
        self.push_screen(InputDialog(f"Add Tag to sample {sample_id}", "Enter tag name...", handle_tag))

    def prompt_rating(self, sample_id: str) -> None:
        def handle_rating(rating: str):
            if rating.strip():
                try:
                    val = int(rating)
                    result = self.controller.handle_input(f"rate {sample_id} {val}")
                    self.log_result(result)
                    self.action_refresh_samples()
                except ValueError:
                    self.log_result("Error: Rating must be a number 1-5")
        
        self.push_screen(InputDialog(f"Rate sample {sample_id} (1-5)", "Enter rating...", handle_rating))

    def prompt_search(self) -> None:
        def handle_search(query: str):
            if query.strip():
                self.perform_search(query)
        
        self.push_screen(InputDialog("Search Samples", "Enter search query...", handle_search))

    def action_show_command_bar(self) -> None:
        self.push_screen(CommandScreen())

    def action_toggle_playback(self, sample_id: str, is_auto: bool = False) -> None:
        """Play or stop the selected sample. is_auto is True when triggered by navigation."""
        if self.player.is_playing():
            self.player.stop()
            if not is_auto:
                # Manual stop exits audition mode
                self.audition_mode = False
                return

        if not is_auto:
            # Manual start enters audition mode
            self.audition_mode = True

        sample = get_sample_by_id(sample_id)
        if sample:
            path = sample["path"]
            if not self.player.play(path):
                self.log_result(f"Error: Playback failed for {path}")
                self.audition_mode = False
            else:
                self.log_result(f"Playing: {os.path.basename(path)}")

    def handle_command_text(self, cmd_text: str) -> None:
        cmd_text = cmd_text.strip()
        if not cmd_text:
            return

        # Known base commands
        base_commands = {"scan", "rescan", "list", "dirs", "add-dir", "rm-dir", "tag", "rate", "stats", "search"}
        first_word = cmd_text.split()[0].lower() if cmd_text.split() else ""

        # Intercept search for better UI experience
        if first_word == "search":
            query = cmd_text[7:].strip()
            self.perform_search(query)
            return
        
        # Handle bulk-tag separately to use advanced parser if needed
        if first_word == "bulk-tag":
            parts = cmd_text.split(None, 2)
            if len(parts) >= 3:
                query = parts[1]
                tag = parts[2]
                self.perform_bulk_tag(query, tag)
                return
            else:
                self.log_result("Error: bulk-tag requires <query> <tag>")
                return
        
        # Auto-detect filtering if it contains a colon and isn't a known command
        if ":" in cmd_text and first_word not in base_commands:
            self.perform_search(cmd_text)
            return

        # Handle other commands via controller
        result = self.controller.handle_input(cmd_text)
        self.log_result(result)
        
        # If command might change data, refresh list
        if any(keyword in cmd_text.lower() for keyword in ("scan", "tag", "rate", "unrate", "rm-dir")):
            self.action_refresh_samples()

    @on(Input.Submitted)
    def handle_command(self, event: Input.Submitted) -> None:
        # This is for any Inputs in the app that might submit
        # But our main one is in CommandScreen now.
        pass

    def perform_search(self, query: str) -> None:
        self.last_query = query
        # Complex parser for query
        filters = {}
        sort_by = "filename"
        sort_order = "ASC"

        parts = query.split()
        remaining_query = []

        for part in parts:
            part = part.strip(",") # Handle tag:kick, etc
            if ":" in part:
                key, val = part.split(":", 1)
                if key == "tag":
                    filters["tag"] = val
                elif key == "type":
                    filters["type"] = val
                elif key == "rating":
                    # Handle rating:>3 etc
                    import re
                    match = re.match(r"([><=]{1,2})?(\d)", val)
                    if match:
                        op = match.group(1) or "="
                        filters["rating"] = (op, int(match.group(2)))
                elif key == "sort":
                    sort_by = val.lower()
                    if sort_by.startswith("-"):
                        sort_by = sort_by[1:]
                        sort_order = "DESC"
            else:
                remaining_query.append(part)
        
        if remaining_query:
            filters["query"] = " ".join(remaining_query)

        # Find the active table (could be on the main screen or a pushed screen)
        target_table = None
        for screen in reversed(self.screen_stack):
            try:
                target_table = screen.query_one(SampleTable)
                break
            except:
                continue

        if not target_table:
            return
             
        target_table.clear()
        results = search_samples(filters, sort_by=sort_by, sort_order=sort_order)
        for s in results:
            target_table.add_row(
                str(s["id"]),
                s["filename"],
                s["tags"] or "",
                str(s["rating"]) if s["rating"] is not None else "",
                str(s["bpm"]) if s["bpm"] is not None else "",
                s["created_at"][:10] if s["created_at"] else ""
            )
        
        filter_summary = ", ".join([f"{k}:{v}" for k,v in filters.items()])
        self.log_result(f"Search results for [{filter_summary}] (Sort: {sort_by}): {len(results)}")

    def perform_bulk_tag(self, query: str, tag: str) -> None:
        """Apply a tag to all samples matching a query."""
        # Use our existing complex parser logic via a helper or just re-parse
        # For simplicity, we'll re-parse or use the perform_search logic
        
        # We need results, so let's extract the parsing logic if we had time, 
        # but for now we'll just run search_samples with the filters.
        
        # Re-use parsing logic (ideally this should be a static method)
        filters = {}
        parts = query.split()
        remaining_query = []
        for part in parts:
            part = part.strip(",")
            if ":" in part:
                key, val = part.split(":", 1)
                # ... rating/type/tag logic ...
                # (Duplicating for now, refactoring later)
                if key == "tag": filters["tag"] = val
                elif key == "type": filters["type"] = val
                elif key == "rating":
                    import re
                    match = re.match(r"([><=]{1,2})?(\d)", val)
                    if match:
                        op = match.group(1) or "="
                        filters["rating"] = (op, int(match.group(2)))
            else:
                remaining_query.append(part)
        if remaining_query:
            filters["query"] = " ".join(remaining_query)

        results = search_samples(filters)
        if not results:
            self.log_result(f"No samples found matching '{query}'. Bulk tag aborted.")
            return

        from sample_manager.db.tag_repository import add_tag_to_sample
        for s in results:
            add_tag_to_sample(s["id"], tag)
        
        self.log_result(f"Bulk tagged {len(results)} samples with '{tag}'.")
        self.action_refresh_samples()

if __name__ == "__main__":
    app = SampleManagerApp()
    app.run()
