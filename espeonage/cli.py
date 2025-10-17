#!/usr/bin/env python3
"""
Command-line interface for Espeonage
"""

import argparse
import json
import sys
from .replay_parser import ReplayParser
from .battle_simulator import BattleSimulator


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Espeonage - Pokémon Showdown replay parser and battle simulator'
    )
    
    parser.add_argument(
        'replay',
        help='Path to replay file or URL to replay'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file for results (default: stdout)',
        default=None
    )
    
    parser.add_argument(
        '-f', '--format',
        help='Output format (json, text)',
        choices=['json', 'text'],
        default='text'
    )
    
    parser.add_argument(
        '--verbose',
        help='Verbose output',
        action='store_true'
    )
    
    args = parser.parse_args()
    
    # Parse the replay
    parser_obj = ReplayParser()
    
    try:
        if args.replay.startswith('http://') or args.replay.startswith('https://'):
            if args.verbose:
                print(f"Fetching replay from URL: {args.replay}", file=sys.stderr)
            replay_data = parser_obj.parse_replay_url(args.replay)
        else:
            if args.verbose:
                print(f"Parsing replay file: {args.replay}", file=sys.stderr)
            replay_data = parser_obj.parse_replay_file(args.replay)
    except Exception as e:
        print(f"Error parsing replay: {e}", file=sys.stderr)
        sys.exit(1)
    
    if 'error' in replay_data:
        print(f"Error: {replay_data['error']}", file=sys.stderr)
        sys.exit(1)
    
    # Simulate the battle
    simulator = BattleSimulator()
    battle_log = replay_data.get('battle_log', [])
    
    if args.verbose:
        print(f"Processing {len(battle_log)} log entries...", file=sys.stderr)
    
    results = simulator.process_battle_log(battle_log)
    
    # Add metadata to results
    results['metadata'] = replay_data.get('metadata', {})
    
    # Format output
    if args.format == 'json':
        output = json.dumps(results, indent=2)
    else:
        output = format_text_output(results)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        if args.verbose:
            print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)


def format_text_output(results: dict) -> str:
    """Format results as human-readable text"""
    lines = []
    
    # Metadata
    metadata = results.get('metadata', {})
    if metadata:
        lines.append("=" * 60)
        lines.append("REPLAY INFORMATION")
        lines.append("=" * 60)
        if 'format' in metadata:
            lines.append(f"Format: {metadata['format']}")
        if 'players' in metadata:
            lines.append(f"Players: {', '.join(metadata['players'])}")
        if 'rating' in metadata and metadata['rating']:
            lines.append(f"Rating: {metadata['rating']}")
        lines.append("")
    
    # Teams
    teams = results.get('teams', {})
    pokemon_data = results.get('pokemon', {})
    
    for player, team in teams.items():
        lines.append("=" * 60)
        lines.append(f"TEAM {player.upper()}")
        lines.append("=" * 60)
        
        for pokemon_name in team:
            pokemon_id = f"{player}:{pokemon_name}"
            if pokemon_id in pokemon_data:
                data = pokemon_data[pokemon_id]
                lines.append(f"\n{data['name']} ({data['species']}) - Level {data['level']}")
                lines.append("-" * 40)
                
                if data['ability']:
                    lines.append(f"  Ability: {data['ability']}")
                if data['item']:
                    lines.append(f"  Item: {data['item']}")
                if data['moves']:
                    lines.append(f"  Moves: {', '.join(data['moves'])}")
                
                lines.append(f"  Stats:")
                lines.append(f"    K/D Ratio: {data['kd_ratio']:.2f} ({data['knockouts']}/{data['deaths']})")
                lines.append(f"    Damage Dealt: {data['damage_dealt']}")
                lines.append(f"    Damage Taken: {data['damage_taken']}")
        
        lines.append("")
    
    return "\n".join(lines)


if __name__ == '__main__':
    main()
