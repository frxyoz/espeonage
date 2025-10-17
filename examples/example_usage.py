#!/usr/bin/env python3
"""
Example usage of the Espeonage library
"""

from espeonage import ReplayParser, BattleSimulator
import json


def main():
    # Example 1: Parse a local replay file
    print("=" * 60)
    print("Example 1: Parsing local replay file")
    print("=" * 60)
    
    parser = ReplayParser()
    replay_data = parser.parse_replay_file('examples/example_replay.log')
    
    print(f"Metadata: {json.dumps(replay_data['metadata'], indent=2)}")
    print(f"Battle log entries: {len(replay_data['battle_log'])}")
    
    # Example 2: Simulate the battle
    print("\n" + "=" * 60)
    print("Example 2: Simulating battle")
    print("=" * 60)
    
    simulator = BattleSimulator()
    results = simulator.process_battle_log(replay_data['battle_log'])
    
    print("\nPokémon Summary:")
    for pokemon_id, data in results['pokemon'].items():
        print(f"\n{data['name']} ({data['species']})")
        print(f"  Moves: {', '.join(data['moves']) if data['moves'] else 'None revealed'}")
        print(f"  Ability: {data['ability'] or 'Unknown'}")
        print(f"  Item: {data['item'] or 'Unknown'}")
        print(f"  K/D Ratio: {data['kd_ratio']:.2f} ({data['knockouts']}/{data['deaths']})")
        print(f"  Damage: {data['damage_dealt']} dealt, {data['damage_taken']} taken")
    
    # Example 3: Get team information
    print("\n" + "=" * 60)
    print("Example 3: Team information")
    print("=" * 60)
    
    tracker = simulator.get_tracker()
    for player in ['p1', 'p2']:
        team = tracker.get_team(player)
        print(f"\nTeam {player.upper()}:")
        for pokemon in team:
            print(f"  - {pokemon.name} (Level {pokemon.level})")
    
    # Example 4: Using the damage calculator
    print("\n" + "=" * 60)
    print("Example 4: Damage calculator (requires Node.js)")
    print("=" * 60)
    
    from espeonage import DamageCalculator
    
    calc = DamageCalculator()
    
    # Example calculation
    attacker = {
        'species': 'Garchomp',
        'level': 100,
        'ability': 'Rough Skin',
        'nature': 'Jolly',
        'evs': {'hp': 0, 'atk': 252, 'def': 4, 'spa': 0, 'spd': 0, 'spe': 252}
    }
    
    defender = {
        'species': 'Ferrothorn',
        'level': 100,
        'ability': 'Iron Barbs',
        'nature': 'Relaxed',
        'evs': {'hp': 252, 'atk': 0, 'def': 252, 'spa': 0, 'spd': 4, 'spe': 0}
    }
    
    result = calc.calculate_damage(attacker, defender, 'Earthquake')
    
    if 'error' in result:
        print(f"  Calculator not available: {result['error']}")
        print("  (Install Node.js dependencies with: npm install)")
    else:
        print(f"  Damage range: {result.get('damageRange', 'N/A')}")
        print(f"  Description: {result.get('description', 'N/A')}")


if __name__ == '__main__':
    main()
