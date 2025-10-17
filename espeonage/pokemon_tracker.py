"""
Pokémon tracker for tracking revealed information during battle
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field


@dataclass
class PokemonData:
    """Data structure for tracking Pokémon information"""
    name: str
    species: str = ""
    level: int = 100
    gender: str = ""
    
    # Revealed information
    moves: Set[str] = field(default_factory=set)
    ability: Optional[str] = None
    item: Optional[str] = None
    
    # Stats tracking
    hp_max: Optional[int] = None
    hp_current: Optional[int] = None
    
    # Battle statistics
    knockouts: int = 0
    deaths: int = 0
    damage_dealt: int = 0
    damage_taken: int = 0
    
    # EV/IV inference data
    observed_stats: Dict[str, List[int]] = field(default_factory=dict)
    
    def add_move(self, move: str):
        """Add a revealed move"""
        self.moves.add(move)
    
    def set_ability(self, ability: str):
        """Set the Pokémon's ability"""
        self.ability = ability
    
    def set_item(self, item: str):
        """Set the Pokémon's item"""
        self.item = item
    
    def update_hp(self, hp: int, max_hp: int):
        """Update HP information"""
        self.hp_current = hp
        self.hp_max = max_hp
    
    def add_knockout(self):
        """Increment knockout counter"""
        self.knockouts += 1
    
    def add_death(self):
        """Increment death counter"""
        self.deaths += 1
    
    def record_damage_dealt(self, damage: int):
        """Record damage dealt to opponent"""
        self.damage_dealt += damage
    
    def record_damage_taken(self, damage: int):
        """Record damage taken"""
        self.damage_taken += damage
    
    def get_kd_ratio(self) -> float:
        """Calculate K/D ratio"""
        if self.deaths == 0:
            return float(self.knockouts)
        return self.knockouts / self.deaths


class PokemonTracker:
    """Tracker for Pokémon information during battle simulation"""
    
    def __init__(self):
        self.pokemon: Dict[str, PokemonData] = {}
        self.teams: Dict[str, List[str]] = {'p1': [], 'p2': []}
        
    def register_pokemon(self, player: str, position: str, name: str, details: str = ""):
        """
        Register a new Pokémon
        
        Args:
            player: Player identifier (p1, p2, etc.)
            position: Position identifier (p1a, p2b, etc.)
            name: Pokémon nickname
            details: Species and other details
        """
        pokemon_id = f"{player}:{name}"
        
        if pokemon_id not in self.pokemon:
            # Parse details: "species, L##, gender"
            species = name
            level = 100
            gender = ""
            
            if details:
                parts = details.split(', ')
                if parts:
                    species = parts[0]
                for part in parts[1:]:
                    if part.startswith('L'):
                        try:
                            level = int(part[1:])
                        except ValueError:
                            pass
                    elif part in ['M', 'F']:
                        gender = part
            
            self.pokemon[pokemon_id] = PokemonData(
                name=name,
                species=species,
                level=level,
                gender=gender
            )
            
            if pokemon_id not in self.teams[player]:
                self.teams[player].append(pokemon_id)
    
    def track_move(self, user: str, move: str):
        """
        Track a move used by a Pokémon
        
        Args:
            user: Pokémon identifier
            move: Move name
        """
        if user in self.pokemon:
            self.pokemon[user].add_move(move)
    
    def track_ability(self, pokemon: str, ability: str):
        """
        Track a revealed ability
        
        Args:
            pokemon: Pokémon identifier
            ability: Ability name
        """
        if pokemon in self.pokemon:
            self.pokemon[pokemon].set_ability(ability)
    
    def track_item(self, pokemon: str, item: str):
        """
        Track a revealed item
        
        Args:
            pokemon: Pokémon identifier
            item: Item name
        """
        if pokemon in self.pokemon:
            self.pokemon[pokemon].set_item(item)
    
    def track_hp(self, pokemon: str, hp: int, max_hp: int):
        """
        Track HP changes
        
        Args:
            pokemon: Pokémon identifier
            hp: Current HP
            max_hp: Maximum HP
        """
        if pokemon in self.pokemon:
            self.pokemon[pokemon].update_hp(hp, max_hp)
    
    def track_faint(self, pokemon: str):
        """
        Track when a Pokémon faints
        
        Args:
            pokemon: Pokémon identifier
        """
        if pokemon in self.pokemon:
            self.pokemon[pokemon].add_death()
            # The last attacker gets credit for the knockout
            # This would be tracked separately in battle simulation
    
    def track_knockout(self, pokemon: str):
        """
        Track when a Pokémon gets a knockout
        
        Args:
            pokemon: Pokémon identifier
        """
        if pokemon in self.pokemon:
            self.pokemon[pokemon].add_knockout()
    
    def track_damage(self, attacker: str, defender: str, damage: int):
        """
        Track damage dealt and taken
        
        Args:
            attacker: Attacking Pokémon identifier
            defender: Defending Pokémon identifier
            damage: Amount of damage
        """
        if attacker in self.pokemon:
            self.pokemon[attacker].record_damage_dealt(damage)
        if defender in self.pokemon:
            self.pokemon[defender].record_damage_taken(damage)
    
    def get_pokemon(self, pokemon_id: str) -> Optional[PokemonData]:
        """Get Pokémon data by identifier"""
        return self.pokemon.get(pokemon_id)
    
    def get_team(self, player: str) -> List[PokemonData]:
        """Get all Pokémon for a player"""
        return [self.pokemon[pid] for pid in self.teams.get(player, []) if pid in self.pokemon]
    
    def get_all_pokemon(self) -> List[PokemonData]:
        """Get all tracked Pokémon"""
        return list(self.pokemon.values())
    
    def get_summary(self) -> Dict:
        """Get a summary of all tracked Pokémon"""
        summary = {}
        for pokemon_id, data in self.pokemon.items():
            summary[pokemon_id] = {
                'name': data.name,
                'species': data.species,
                'level': data.level,
                'moves': list(data.moves),
                'ability': data.ability,
                'item': data.item,
                'knockouts': data.knockouts,
                'deaths': data.deaths,
                'kd_ratio': data.get_kd_ratio(),
                'damage_dealt': data.damage_dealt,
                'damage_taken': data.damage_taken,
            }
        return summary
