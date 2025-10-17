# Espeonage Replay Parser

The replay parser module provides robust parsing capabilities for Pokémon Showdown replay data.

## Features

- **Multiple Input Formats**: Parse HTML pages, JSON files, and raw log text
- **Robust HTML Extraction**: Supports various inline script patterns (Replays.embed, Replays.append, Replays.render)
- **JSON Endpoint Fallback**: Automatically tries .json endpoint if HTML parsing fails
- **Chat/UI Filtering**: Filters out chat messages and UI-only content
- **Terminal Command Detection**: Stops parsing at battle end commands (win, tie, forcewin)

## Installation

```python
from espeonage.replay_parser import ReplayParser
```

## Usage

### Parse from URL

```python
parser = ReplayParser()
result = parser.parse_replay_url('https://replay.pokemonshowdown.com/gen9ou-2172099392')

if 'error' not in result:
    print(f"Format: {result['metadata']['format']}")
    print(f"Players: {result['metadata']['p1']} vs {result['metadata']['p2']}")
    print(f"Total moves: {len(result['battle_log'])}")
```

### Parse from Local File

```python
parser = ReplayParser()

# Supports HTML, JSON, or raw log files
result = parser.parse_replay_file('replay.html')
result = parser.parse_replay_file('replay.json')
result = parser.parse_replay_file('replay.log')
```

### Parse Raw Log Text

```python
parser = ReplayParser()
log_text = """
|player|p1|Alice|avatar
|player|p2|Bob|avatar
|turn|1
|switch|p1a: Pikachu|Pikachu, L50|150/150
|win|Alice
"""

result = parser.parse_raw_log(log_text)
```

## Output Format

The parser returns a dictionary with two keys:

- `metadata`: Dict containing replay information (id, format, players, etc.)
- `battle_log`: List of parsed log entries, each with:
  - `command`: The battle command (e.g., 'move', 'switch', 'win')
  - `args`: List of command arguments
  - `raw`: Original log line

Example:
```python
{
    'metadata': {
        'id': 'gen9ou-2172099392',
        'format': 'gen9ou',
        'p1': 'Player1',
        'p2': 'Player2'
    },
    'battle_log': [
        {
            'command': 'player',
            'args': ['p1', 'Player1', 'avatar'],
            'raw': '|player|p1|Player1|avatar'
        },
        # ... more entries
    ]
}
```

## Error Handling

If parsing fails, the parser returns a dictionary with an 'error' key:

```python
result = parser.parse_replay_html(invalid_html)
# Returns: {'error': 'Could not parse replay data'}
```

## Running Tests

```bash
python -m unittest tests.test_replay_parser -v
```

## Examples

See `example_usage.py` for complete working examples.
