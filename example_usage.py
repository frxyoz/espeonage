"""
Example usage of the Espeonage replay parser.
"""

from espeonage.replay_parser import ReplayParser


def main():
    parser = ReplayParser()
    
    # Example 1: Parse from a local HTML file
    print("Example 1: Parsing HTML file with Replays.append pattern")
    result = parser.parse_replay_file('tests/fixtures/replay_append.html')
    if 'error' not in result:
        print(f"  Format: {result['metadata'].get('format')}")
        print(f"  Players: {result['metadata'].get('p1')} vs {result['metadata'].get('p2')}")
        print(f"  Battle log entries: {len(result['battle_log'])}")
        print(f"  Winner: {result['battle_log'][-1]['args'][0] if result['battle_log'] else 'N/A'}")
    print()
    
    # Example 2: Parse from a JSON file
    print("Example 2: Parsing JSON file")
    result = parser.parse_replay_file('tests/fixtures/replay.json')
    if 'error' not in result:
        print(f"  Format: {result['metadata'].get('format')}")
        print(f"  Players: {result['metadata'].get('p1')} vs {result['metadata'].get('p2')}")
        print(f"  Battle log entries: {len(result['battle_log'])}")
    print()
    
    # Example 3: Parse raw log text
    print("Example 3: Parsing raw log text")
    raw_log = """
|player|p1|Alice|avatar
|player|p2|Bob|avatar
|turn|1
|switch|p1a: Pikachu|Pikachu, L50|150/150
|switch|p2a: Charizard|Charizard, L50|200/200
|c|Alice|Good luck!
|c|Bob|You too!
|turn|2
|move|p1a: Pikachu|Thunderbolt|p2a: Charizard
|-damage|p2a: Charizard|0 fnt
|faint|p2a: Charizard
|win|Alice
""".strip()
    
    result = parser.parse_raw_log(raw_log)
    print(f"  Battle log entries: {len(result['battle_log'])}")
    print(f"  Chat messages filtered: Yes (none in battle_log)")
    print(f"  Last command: {result['battle_log'][-1]['command']}")
    print()
    
    # Example 4: Parse from URL (would require network access)
    print("Example 4: Parsing from URL")
    print("  # This requires network access:")
    print("  # result = parser.parse_replay_url('https://replay.pokemonshowdown.com/gen9ou-2172099392')")
    print("  # The parser will try HTML first, then fall back to .json endpoint if needed")


if __name__ == '__main__':
    main()
