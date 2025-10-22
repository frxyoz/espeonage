<div align="center">
  <h1>Espeonage</h1>
  ![Espeonage Logo](assets/logo.png)
  <p><i>
    “A Future Sight for your next matchup!”
  </i>
  </p>
  <p>
    <i>
      A hybrid Python + Node.js tool that parses Pokémon Showdown replays, simulates battle progress, 
      and infers each Pokémon's potential items, EV spreads, and K/D ratios using Smogon's official damage calculation engine.
    </i>
  </p>
</div>


## Features

- **Replay Parsing**: Parse Pokémon Showdown replays from URLs, HTML files, or battle log files
- **Battle Simulation**: Simulate battle progress and track all revealed information
- **Pokémon Tracking**: Track moves, abilities, items, and statistics for each Pokémon
- **K/D Ratio Calculation**: Calculate kill/death ratios for competitive analysis
- **Damage Calculation**: Integration with Smogon's official damage calculator
- **EV/IV Inference**: Framework for inferring EV spreads based on observed damage

## Installation

### Prerequisites

- Python 3.7+
- Node.js 14+ (for damage calculator integration)

### Install Python Package

```bash
pip install -r requirements.txt
pip install -e .
```

### Install Node.js Dependencies

```bash
npm install
```

This will install the `@smogon/calc` package for damage calculations.

## Usage

### Command Line Interface

Parse and analyze a replay:

```bash
# From a local file
espeonage examples/example_replay.log

# From a URL
espeonage https://replay.pokemonshowdown.com/gen9ou-123456789

# Output to JSON
espeonage examples/example_replay.log -f json -o output.json

# Verbose mode
espeonage examples/example_replay.log --verbose
```

### Python Library

```python
from espeonage import ReplayParser, BattleSimulator

# Parse a replay
parser = ReplayParser()
replay_data = parser.parse_replay_file('replay.log')

# Simulate the battle
simulator = BattleSimulator()
results = simulator.process_battle_log(replay_data['battle_log'])

# Get Pokémon information
for pokemon_id, data in results['pokemon'].items():
    print(f"{data['name']}: {data['moves']}")
    print(f"K/D Ratio: {data['kd_ratio']}")
```

### Damage Calculator

```python
from espeonage import DamageCalculator

calc = DamageCalculator()

attacker = {
    'species': 'Garchomp',
    'level': 100,
    'ability': 'Rough Skin',
    'nature': 'Jolly',
    'evs': {'hp': 0, 'atk': 252, 'def': 4, 'spa': 0, 'spd': 0, 'spe': 252},
}

defender = {
    'species': 'Landorus-Therian',
    'level': 100,
    'ability': 'Intimidate',
    'evs': {'hp': 252, 'atk': 4, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 252},
}

result = calc.calculate_damage(attacker, defender, 'Earthquake')
print(result['damageRange'])
```

## Architecture

### Python Components

- **`replay_parser.py`**: Parses Pokémon Showdown replay files and URLs
- **`pokemon_tracker.py`**: Tracks revealed Pokémon information (moves, abilities, items)
- **`battle_simulator.py`**: Processes battle logs and simulates battle state
- **`damage_calculator.py`**: Python interface to Node.js damage calculator
- **`cli.py`**: Command-line interface

### Node.js Components

- **`calc_wrapper.js`**: Wrapper script for `@smogon/calc` damage calculator

## Tracked Information

For each Pokémon in a battle, Espeonage tracks:

- **Species and Details**: Name, species, level, gender
- **Moves**: All revealed moves
- **Ability**: Revealed ability
- **Item**: Revealed held item
- **HP**: Current and maximum HP
- **Battle Statistics**:
  - Knockouts (kills)
  - Deaths (faints)
  - K/D Ratio
  - Damage dealt
  - Damage taken

## Examples

See the `examples/` directory for:

- `example_replay.log`: Sample battle log file
- `example_usage.py`: Comprehensive usage examples

Run the example:

```bash
cd /path/to/espeonage
python examples/example_usage.py
```

## Development

### Project Structure

```
espeonage/
├── espeonage/          # Python package
│   ├── __init__.py
│   ├── replay_parser.py
│   ├── pokemon_tracker.py
│   ├── battle_simulator.py
│   ├── damage_calculator.py
│   └── cli.py
├── calc_wrapper.js     # Node.js damage calculator wrapper
├── examples/           # Example files
├── package.json        # Node.js dependencies
├── requirements.txt    # Python dependencies
├── setup.py           # Python package setup
└── README.md
```

## Credits

- Damage calculations powered by [Smogon's damage calculator](https://github.com/smogon/damage-calc)
- Pokémon Showdown replay format

## License

See LICENSE file for details.
