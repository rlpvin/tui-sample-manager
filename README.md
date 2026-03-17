# TUI Sample Manager

A keyboard-first terminal-based audio sample manager for music producers and sound designers. Organize, preview, and manage your samples right from the terminal.

## Features

- Fast indexing of large sample libraries
- Search by keyword, filter and sort by column
- Low-latency audio playback directly from the terminal (macOS/Linux)
- Automatic BPM and Key detection using Librosa
- Batch operations: tag, rename, covert format
- Duplicate detection based on SHA-256 hashing.
- Atomic database transactions to prevent corruption.

## Installation

### Prerequisites

- Python 3.9+
- **macOS**: `afplay` (pre-installed)
- **Linux**: `aplay` (ALSA) or `play` (SoX)

### One-Step Install (Direct from GitHub)

```bash
pip install git+https://github.com/rlpvin/tui-sample-manager.git
```

### Development Install

```bash
git clone https://github.com/rlpvin/tui-sample-manager.git
cd tui-sample-manager
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Quick Start

Launch the manager from any terminal:

```bash
sample-manager
```

### Common Commands (inside the TUI):

- `add-dir` - Add/register sample directory.
- `scan` - Scan registered directoriees and index samples.
- `scan --analyze` - Detect BPM and Key for all samples.
- `search <keyword>` - Search sample list based on filename.

### Keyboard Actions (inside the TUI):

- `h` - Show help page
- `f` - Focus command input
- `Arrow keys` - Navigate sample list
- `Space` - Yoggle preview
- `t` - Add tag to focussed sample
- `r` - Rate focussed sample
- `^p` - Settings page
- `q` - Quit

### Batch operations (inside the TUI):

- `bulk-tag <query> <tag>` - Add a tag to all samples where filename contains query.
- `bulk-rename <query> <name>` - Rename all samples where filename contains query.
- `bulk-convert <query> <ext>` - Convert all samples where filename contains query.

## Development

Run the test suite:

```bash
pytest
```

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
sample-manager --debug
```
