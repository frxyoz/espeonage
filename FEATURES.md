# Espeonage Features

This document provides a comprehensive overview of all features available in Espeonage.

## Core Features

### 1. Replay Parsing

Espeonage can parse Pokémon Showdown replays from multiple sources:

- **Local battle log files** (`.log` format)
- **HTML replay files** (saved from replay.pokemonshowdown.com)
- **Direct URLs** (e.g., `https://replay.pokemonshowdown.com/gen9ou-123456789`)
- **JSON replay data** (raw replay data format)

Example:
```python
from espeonage import ReplayParser

parser = ReplayParser()

# From file
replay_data = parser.parse_replay_file('replay.log')

# From URL
replay_data = parser.parse_replay_url('https://replay.pokemonshowdown.com/...')
```

### 2. Battle Simulation

The battle simulator processes the replay log and tracks all events:

- Pokémon switches and team composition
- Move usage
- Damage calculations
- Ability reveals
- Item reveals
- HP changes
- Faint events

Example:
```python
from espeonage import BattleSimulator

simulator = BattleSimulator()
results = simulator.process_battle_log(replay_data['battle_log'])
```

### 3. Pokémon Tracking

Track detailed information about each Pokémon:

#### Tracked Data
- **Basic Info**: Species, nickname, level, gender
- **Revealed Moves**: All moves used during battle
- **Ability**: Revealed ability
- **Item**: Revealed held item
- **HP Stats**: Current and maximum HP
- **Battle Stats**:
  - Knockouts (kills)
  - Deaths (faints)
  - K/D Ratio
  - Total damage dealt
  - Total damage taken

Example:
```python
tracker = simulator.get_tracker()
pokemon = tracker.get_pokemon('p1:Garchomp')

print(f"Moves: {pokemon.moves}")
print(f"Ability: {pokemon.ability}")
print(f"K/D Ratio: {pokemon.get_kd_ratio()}")
```

### 4. K/D Ratio Calculation

Kill/Death ratios are automatically calculated for each Pokémon:

- **K/D = Knockouts / Deaths**
- If deaths = 0, K/D = knockouts (e.g., 3.00 for 3 KOs)
- Useful for competitive analysis and team performance evaluation

### 5. Damage Calculator Integration

Integration with Smogon's official damage calculator (`@smogon/calc`):

Features:
- Accurate damage range calculations
- Support for all generations
- Considers EVs, IVs, natures, abilities, items
- Field conditions support
- KO chance calculations

Example:
```python
from espeonage import DamageCalculator

calc = DamageCalculator()

attacker = {
    'species': 'Garchomp',
    'level': 100,
    'ability': 'Rough Skin',
    'nature': 'Jolly',
    'evs': {'hp': 0, 'atk': 252, 'def': 4, 'spa': 0, 'spd': 0, 'spe': 252}
}

defender = {
    'species': 'Landorus-Therian',
    'level': 100,
    'ability': 'Intimidate',
    'evs': {'hp': 252, 'atk': 4, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 252}
}

result = calc.calculate_damage(attacker, defender, 'Earthquake')
print(result['damageRange'])  # e.g., [85, 101]
print(result['description'])  # Full damage calc description
```

### 6. EV/IV Inference Framework

Framework for inferring EV spreads based on observed data:

- Track observed HP values
- Track observed damage amounts
- Compare against calculator to estimate spreads

*Note: Full EV/IV inference algorithm is a placeholder for future implementation.*

### 7. Command-Line Interface

Full-featured CLI for easy replay analysis:

```bash
# Parse a replay
espeonage examples/example_replay.log

# Output to JSON
espeonage replay.log -f json -o output.json

# Verbose mode
espeonage replay.log --verbose

# From URL
espeonage https://replay.pokemonshowdown.com/gen9ou-123456789
```

Output formats:
- **Text**: Human-readable summary with team breakdowns
- **JSON**: Structured data for programmatic use

## Data Structures

### PokemonData

```python
@dataclass
class PokemonData:
    name: str                      # Nickname
    species: str                   # Species name
    level: int                     # Level (default 100)
    gender: str                    # 'M', 'F', or ''
    moves: Set[str]                # Revealed moves
    ability: Optional[str]         # Revealed ability
    item: Optional[str]            # Revealed item
    hp_max: Optional[int]          # Maximum HP
    hp_current: Optional[int]      # Current HP
    knockouts: int                 # Number of KOs
    deaths: int                    # Number of faints
    damage_dealt: int              # Total damage dealt
    damage_taken: int              # Total damage taken
```

### Battle Log Entry

```python
{
    'type': 'move',           # Command type
    'args': ['p1a: Garchomp', 'Earthquake', 'p2a: Landorus'],
    'raw': '|move|p1a: Garchomp|Earthquake|p2a: Landorus'
}
```

### Results Format

```python
{
    'pokemon': {
        'p1:Garchomp': {
            'name': 'Garchomp',
            'species': 'Garchomp',
            'level': 100,
            'moves': ['Earthquake', 'Dragon Claw'],
            'ability': 'Rough Skin',
            'item': 'Choice Scarf',
            'knockouts': 2,
            'deaths': 1,
            'kd_ratio': 2.0,
            'damage_dealt': 250,
            'damage_taken': 150
        },
        # ... more Pokémon
    },
    'teams': {
        'p1': ['Garchomp', 'Toxapex', 'Rotom'],
        'p2': ['Landorus', 'Ferrothorn', 'Heatran']
    },
    'metadata': {
        'format': '[Gen 9] OU',
        'players': ['Player1', 'Player2'],
        'rating': 1500
    }
}
```

## Use Cases

### 1. Competitive Analysis
- Analyze team performance
- Track K/D ratios across multiple battles
- Identify which Pokémon are most effective

### 2. Team Building
- See what moves/items opponents commonly use
- Analyze damage outputs for threat assessment
- Plan counters based on observed spreads

### 3. Replay Review
- Study your own battles for improvement
- Review opponent strategies
- Share structured battle data

### 4. Statistical Analysis
- Aggregate data from multiple replays
- Track meta trends
- Analyze win conditions

### 5. Content Creation
- Generate battle summaries
- Create highlight reels
- Document competitive matches

## Limitations

- **EV/IV inference**: Currently a framework; full implementation pending
- **Hidden Power type**: Not automatically detected
- **Entry hazards**: Tracked but damage not attributed to setter
- **Weather/terrain effects**: Recognized but not fully integrated
- **Tera types**: Detected but not analyzed for optimal usage

## Future Enhancements

Potential features for future versions:

1. Full EV/IV inference algorithm
2. Set recognition (matching to common sets)
3. Replay database and search
4. Multi-replay analysis
5. Win condition identification
6. Turn-by-turn game state reconstruction
7. Probability-based predictions
8. Team matchup analysis
