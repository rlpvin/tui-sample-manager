import os
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, DataTable
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.screen import Screen
from textual import on

from sample_manager.app.controller import ApplicationController
from sample_manager.db.sample_repository import (
    get_all_samples, 
    search_samples, 
    get_sample_by_id, 
    get_duplicates_grouped, 
    delete_sample
)
from sample_manager.utils.playback import Player
from sample_manager.utils.batch import BatchProcessor

class HelpScreen(Screen):

    def compose(self) -> ComposeResult:
        with Vertical(id="help_container"):
            yield Static("Sample Manager Help", id="help_title")
            with Vertical(id="help_scroll"):
                yield Static(
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
                    "tags              - List all available tags\n"
                    "rate <id> <1-5>   - Rate a sample\n"
                    "unrate <id>       - Remove rating from a sample\n"
                    "bulk-tag <q> <t>  - Tag all samples matching query\n"
                    "bulk-rename <q> <p,r> - Rename samples matching query\n"
                    "bulk-convert <q> <ext> - Convert samples matching query\n"
                    "bulk-normalize <q> [db] - Normalize volume matching query\n"
                    "duplicates        - Find and manage duplicate samples\n"
                    "analyze <id>      - Deep analysis (Key/BPM). Skips one-shots.\n"
                    "scan --analyze    - Library scan with deep analysis enabled\n"
                    "stats             - Show database statistics\n\n"
                    "Advanced Filtering (Search or Command Modal):\n\n"
                    "tag:<name>        - Filter by tag\n"
                    "type:<ext>        - Filter by file extension (wav, mp3...)\n"
                    "rating:<op><val>  - Rating (e.g., rating:>3, rating:5)\n"
                    "bpm:<op><val>     - BPM (e.g., bpm:>120, bpm:115)\n"
                    "key:<key>         - Key (e.g., key:D Minor, key:C#)\n\n"
                    "Sorting:\n\n"
                    "sort:<field>      - Sort by: name, rating, bpm, key, duration\n"
                    "                    Use '-' for descending (e.g., sort:-bpm)\n"
                    "Interactive Sort  - Click any column header to toggle sort\n\n"
                    "Example Query:\n"
                    "tag:kick bpm:>120 type:wav heavy\n\n"
                    "Playback & Analysis:\n\n"
                    "Space             - Play/Pause selected sample\n"
                    "Navigation        - Arrows/PgUp/PgDn automatically plays next\n"
                    "analyze <id>      - Run deep musical analysis (Key/BPM)\n"
                    "scan --analyze    - Full scan with deep analysis enabled\n",
                    id="help_text"
                )
            yield Static("Press any key to close", id="help_footer")

    def on_mount(self) -> None:
        self.styles.background = "rgba(0,0,0,0.8)"

    def on_key(self) -> None:
        self.app.pop_screen()

class ConfirmationDialog(ModalScreen):
    """A modal dialog for Yes/No confirmation."""
    
    def __init__(self, message: str, callback):
        super().__init__()
        self.message = message
        self.callback = callback

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.message, id="dialog_message"),
            Horizontal(
                Static("Press 'y' for Yes, 'n' or Esc for No", id="dialog_footer"),
                id="dialog_buttons"
            ),
            id="dialog_container"
        )

    def on_key(self, event) -> None:
        if event.key == "y":
            self.callback(True)
            self.app.pop_screen()
        elif event.key in ("n", "escape"):
            self.callback(False)
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

    @on(DataTable.HeaderSelected)
    def on_header_clicked(self, event: DataTable.HeaderSelected) -> None:
        """Handle header clicks to sort by the clicked column."""
        # Map labels to field names
        label_map = {
            "ID": "id",
            "Filename": "filename",
            "Tags": "tags",
            "Rating": "rating",
            "BPM": "bpm",
            "Key": "key",
            "Dur": "duration"
        }
        
        column_label = str(event.column_key.value)
        field = label_map.get(column_label)
        
        if field:
            # Toggle direction if clicking same column
            if getattr(self.app, "sort_column", "filename") == field:
                current_dir = getattr(self.app, "sort_direction", "ASC")
                self.app.sort_direction = "DESC" if current_dir == "ASC" else "ASC"
            else:
                self.app.sort_column = field
                self.app.sort_direction = "ASC"
            
            self.app.action_refresh_samples()

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
        table.add_columns("ID", "Filename", "Tags", "Rating", "BPM", "Key", "Dur")
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
        cmd = event.value
        self.app.pop_screen()
        self.app.handle_command_text(cmd)

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

    #duplicates_help {
        width: 100%;
        text-align: center;
    }

    #help_container {
        align: center middle;
        width: 70;
        height: 80%;
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

    #help_scroll {
        overflow-y: auto;
        height: 1fr;
    }

    #help_text {
        height: auto;
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

    #dialog_message {
        text-align: center;
        margin-bottom: 2;
    }

    #dialog_buttons {
        height: auto;
        align: center middle;
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
        self.sort_column = "filename"
        self.sort_direction = "ASC"
        self.current_sample_ids = []
        self.batch_processor = BatchProcessor(log_callback=self.log_result)

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
        table.add_columns("ID", "Filename", "Tags", "Rating", "BPM", "Key", "Dur")
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

    def format_duration(self, seconds: float) -> str:
        """Format duration into a readable string (e.g., 30s, 1m 20s)."""
        if seconds < 60:
            return f"{int(round(seconds))}s"
        
        minutes = int(seconds // 60)
        remaining_seconds = int(round(seconds % 60))
        
        if remaining_seconds == 0:
            return f"{minutes}m"
        return f"{minutes}m {remaining_seconds}s"

    def handle_command_text(self, cmd_text: str) -> None:
        cmd_text = cmd_text.strip()
        if not cmd_text:
            return

        # Known base commands
        base_commands = {
            "scan", "rescan", "list", "dirs", "add-dir", "rm-dir", 
            "tag", "rate", "stats", "search", "duplicates",
            "bulk-tag", "bulk-rename", "bulk-convert", "bulk-normalize"
        }
        first_word = cmd_text.split()[0].lower() if cmd_text.split() else ""

        # Intercept search for better UI experience
        if first_word == "search":
            query = cmd_text[7:].strip()
            self.perform_search(query)
            return
        
        # Handle bulk commands
        if first_word.startswith("bulk-"):
            parts = cmd_text.split(None, 2)
            if len(parts) >= 3:
                query = parts[1]
                param = parts[2]
                if first_word == "bulk-tag":
                    self.perform_bulk_tag(query, param)
                elif first_word == "bulk-rename":
                    self.perform_bulk_rename(query, param)
                elif first_word == "bulk-convert":
                    self.perform_bulk_convert(query, param)
                elif first_word == "bulk-normalize":
                    self.perform_bulk_normalize(query, param)
                return
            elif first_word == "bulk-normalize" and len(parts) == 2:
                # Normalize can have optional DB param
                self.perform_bulk_normalize(parts[1], "-1.5")
                return
            else:
                self.log_result(f"Error: {first_word} requires <query> <parameters>")
                return
        
        # Auto-detect filtering if it contains a colon and isn't a known command
        if ":" in cmd_text and first_word not in base_commands:
            self.perform_search(cmd_text)
            return

        if cmd_text.lower() == "duplicates":
            self.push_screen(DuplicatesScreen())
            return

        if first_word == "analyze":
            parts = cmd_text.split()
            if len(parts) >= 2:
                # analyze <id>
                try:
                    sid = int(parts[1])
                    self.perform_deep_analyze(sid)
                except ValueError:
                    self.log_result("Error: Sample ID must be a number.")
            else:
                self.log_result("Error: analyze requires <id>.")
            return

        if first_word == "scan" and "--analyze" in cmd_text:
            self.log_result("Starting deep scan (BPM/Key detection enabled)...")
            from sample_manager.scanner.indexer import index_samples
            index_samples(analyze=True)
            self.action_refresh_samples()
            return

        if first_word == "rm-dir":
            parts = cmd_text.split()
            if len(parts) >= 2:
                dir_path = " ".join(parts[1:])
                def do_remove(confirmed):
                    if confirmed:
                        try:
                            # Use router or controller
                            result = self.controller.handle_input(f"rm-dir {dir_path}")
                            self.log_result(result)
                            self.action_refresh_samples()
                        except Exception as e:
                            self.log_result(f"Error: {e}")
                self.push_screen(ConfirmationDialog(f"Remove directory '{dir_path}' from library?", do_remove))
            else:
                self.log_result("Error: rm-dir requires <path>.")
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
        sort_by = self.sort_column
        sort_order = self.sort_direction

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
                elif key == "bpm":
                    import re
                    match = re.match(r"([><=]{1,2})?(\d+)", val)
                    if match:
                        op = match.group(1) or "="
                        filters["bpm"] = (op, int(match.group(2)))
                elif key == "key":
                    filters["key"] = val
                elif key == "sort":
                    sort_by = val.lower()
                    if sort_by.startswith("-"):
                        sort_by = sort_by[1:]
                        sort_order = "DESC"
                    # Update global sort state when using command
                    self.sort_column = sort_by
                    self.sort_direction = sort_order
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
        self.current_sample_ids = [s["id"] for s in results]

        for s in results:
            target_table.add_row(
                str(s["id"]),
                s["filename"],
                s["tags"] or "",
                str(s["rating"]) if s["rating"] is not None else "",
                str(s["bpm"]) if s["bpm"] is not None else "",
                s["musical_key"] or "",
                self.format_duration(s["duration"]) if s["duration"] else ""
            )
        
        filter_summary = ", ".join([f"{k}:{v}" for k,v in filters.items()])
        self.log_result(f"Search results for [{filter_summary}] (Sort: {sort_by}): {len(results)}")

    def perform_bulk_tag(self, query: str, tag: str) -> None:
        self.perform_search(query)
        if not self.current_sample_ids:
            self.log_result(f"No samples found for query: {query}")
            return
            
        count = 0
        from sample_manager.db.tag_repository import add_tag_to_sample
        for sid in self.current_sample_ids:
            add_tag_to_sample(sid, tag)
            count += 1
        
        self.log_result(f"Bulk tagged {count} samples with '{tag}'")
        self.action_refresh_samples()

    def perform_bulk_rename(self, query: str, params: str) -> None:
        if "," not in params:
            self.log_result("Error: bulk-rename requires <query> <pattern>,<replacement>")
            return
            
        pattern, replacement = params.split(",", 1)
        self.perform_search(query)
        if not self.current_sample_ids:
            self.log_result(f"No samples found for query: {query}")
            return
            
        count = self.batch_processor.rename_samples(self.current_sample_ids, pattern, replacement)
        self.log_result(f"Bulk renamed {count} samples.")
        self.action_refresh_samples()

    def perform_bulk_convert(self, query: str, target_ext: str) -> None:
        self.perform_search(query)
        if not self.current_sample_ids:
            self.log_result(f"No samples found for query: {query}")
            return
            
        count = self.batch_processor.convert_samples(self.current_sample_ids, target_ext)
        self.log_result(f"Bulk converted {count} samples to {target_ext}.")
        self.action_refresh_samples()

    def perform_bulk_normalize(self, query: str, target_db: str) -> None:
        try:
            db_val = float(target_db)
        except ValueError:
            self.log_result("Error: target_db must be a number.")
            return

        self.perform_search(query)
        if not self.current_sample_ids:
            self.log_result(f"No samples found for query: {query}")
            return
            
        count = self.batch_processor.normalize_samples(self.current_sample_ids, db_val)
        self.log_result(f"Bulk normalized {count} samples to {db_val}dB.")
        self.action_refresh_samples()

    def perform_deep_analyze(self, sample_id: int) -> None:
        from sample_manager.db.sample_repository import get_sample_by_id, bulk_create_samples
        sample = get_sample_by_id(sample_id)
        if not sample:
            self.log_result(f"Sample {sample_id} not found.")
            return
            
        self.log_result(f"Analyzing sample {sample_id} ({sample['filename']})...")
        from sample_manager.scanner.metadata import extract_metadata
        from pathlib import Path
        meta = extract_metadata(Path(sample["path"]), analyze=True)
        
        # Update DB using bulk_create_samples which handles conflict/update
        bulk_create_samples([meta])
        self.log_result(f"Analysis complete: BPM={meta['bpm']}, Key={meta['musical_key']}, Dur={meta['duration']}s")
        self.action_refresh_samples()

class DuplicatesScreen(ModalScreen):
    """Screen for managing duplicate samples."""

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Duplicate Detection & Cleanup", id="duplicates_title"),
            Static("Scanning for bit-for-bit identical files...", id="duplicates_desc"),
            DataTable(id="duplicates_list"),
            Horizontal(
                Static("Press 'd' to delete selected file, 'Esc' to close", id="duplicates_help"),
                id="duplicates_footer"
            ),
            id="duplicates_container"
        )

    def on_mount(self) -> None:
        table = self.query_one("#duplicates_list", DataTable)
        table.add_columns("ID", "Filename", "Path", "Tags", "Rating")
        table.cursor_type = "row"
        self.refresh_duplicates()

    def refresh_duplicates(self) -> None:
        table = self.query_one("#duplicates_list", DataTable)
        table.clear()
        
        duplicate_groups = get_duplicates_grouped()
        
        if not duplicate_groups:
            self.app.notify("No duplicates found!", severity="information")
            self.dismiss()
            return
            
        self.query_one("#duplicates_desc", Static).update(
            f"Found {len(duplicate_groups)} groups of identical files. "
            "Highlight a file and press 'd' to safely remove it from the database."
        )
        self.app.notify(f"Loaded {len(duplicate_groups)} duplicate groups.")

        for group in duplicate_groups:
            # Add a separator row for each hash group
            table.add_row("---", f"Group: {group['hash'][:8]}...", "---", "---", "---")
            for s in group["samples"]:
                table.add_row(
                    str(s["id"]),
                    s["filename"],
                    s["path"],
                    s["tags"] or "",
                    str(s["rating"]) if s["rating"] else ""
                )

    def on_key(self, event) -> None:
        if event.key == "d":
            table = self.query_one("#duplicates_list", DataTable)
            row_key = table.cursor_row
            if row_key is not None:
                row_data = table.get_row_at(row_key)
                sample_id = row_data[0]
                if sample_id == "---":
                    return
                
                def do_delete(confirmed):
                    if confirmed:
                        self.confirm_delete(sample_id, "YES")

                self.app.push_screen(
                    ConfirmationDialog(f"Delete sample {sample_id} from database?", do_delete)
                )
        elif event.key == "escape":
            self.dismiss()

    def confirm_delete(self, sample_id, confirmation):
        if confirmation == "YES":
            try:
                delete_sample(sample_id)
                self.app.notify(f"Sample {sample_id} removed from database.")
                self.refresh_duplicates()
            except Exception as e:
                self.app.notify(f"Error deleting: {e}", severity="error")

if __name__ == "__main__":
    app = SampleManagerApp()
    app.run()
