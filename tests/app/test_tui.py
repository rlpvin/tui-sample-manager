import pytest
from textual.widgets import DataTable
from sample_manager.app.tui import SampleManagerApp, SampleListScreen, CommandScreen, InputDialog, SampleTable
from sample_manager.db.sample_repository import create_sample

@pytest.mark.asyncio
async def test_tui_initial_load(test_db):
    """Test that the TUI loads and displays samples on start."""
    # Add a dummy sample
    create_sample("path/to/test.wav", "test.wav", ".wav", 1024)
    
    app = SampleManagerApp()
    async with app.run_test() as pilot:
        table = app.query_one("#sample_list", SampleTable)
        # Check if row was added
        assert table.row_count == 1
        # Check content
        row_data = table.get_row_at(0)
        assert "test.wav" in row_data

@pytest.mark.asyncio
async def test_tui_full_screen_toggle(test_db):
    """Test that pressing 'l' toggles the full screen list."""
    app = SampleManagerApp()
    async with app.run_test() as pilot:
        # Press 'l' to go to full screen
        await pilot.press("l")
        assert isinstance(app.screen, SampleListScreen)
        
        # Press 'l' again to return
        await pilot.press("l")
        # Check that we are NOT on the SampleListScreen anymore
        assert not isinstance(app.screen, SampleListScreen)

@pytest.mark.asyncio
async def test_tui_command_modal(test_db):
    """Test that pressing 'f' opens the command modal and search works."""
    create_sample("path/to/kick.wav", "kick.wav", ".wav", 2048)
    create_sample("path/to/snare.wav", "snare.wav", ".wav", 3072)
    
    app = SampleManagerApp()
    async with app.run_test() as pilot:
        # Initial check
        table = app.query_one("#sample_list", SampleTable)
        assert table.row_count == 2
        
        # Press 'f' to open command bar
        await pilot.press("f")
        assert isinstance(app.screen, CommandScreen)
        
        # Type search command
        for char in "search kick":
            await pilot.press(char)
        await pilot.press("enter")
        
        # Check if list filtered
        assert table.row_count == 1
        assert "kick.wav" in table.get_row_at(0)

@pytest.mark.asyncio
async def test_tui_shortcuts_tag_rate(test_db):
    """Test that 't' and 'r' shortcuts open the input dialog."""
    create_sample("path/to/test.wav", "test.wav", ".wav", 1024)
    
    app = SampleManagerApp()
    async with app.run_test() as pilot:
        table = app.query_one("#sample_list", SampleTable)
        table.focus()
        
        # Press 't' for tag
        await pilot.press("t")
        assert isinstance(app.screen, InputDialog)
        assert "Add Tag" in app.screen.title_text
        await pilot.press("escape")
        
        # Press 'r' for rate
        await pilot.press("r")
        assert isinstance(app.screen, InputDialog)
        assert "Rate sample" in app.screen.title_text
        await pilot.press("escape")
