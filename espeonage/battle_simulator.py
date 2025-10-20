"""
Battle simulator that processes replay logs and tracks battle state
"""

from typing import Dict, List, Optional
from .pokemon_tracker import PokemonTracker
from .damage_calculator import DamageCalculator


class BattleSimulator:
    """Simulates battle progress from replay logs"""
    
    # Comprehensive list of non-attacking moves to filter out
    NON_ATTACK_MOVES = {
        # Status moves
        'Toxic', 'Thunder Wave', 'Will-O-Wisp', 'Spore', 'Sleep Powder', 'Stun Spore',
        'Hypnosis', 'Yawn', 'Poison Powder', 'Glare', 'Paralyze', 'Confuse Ray',
        'Supersonic', 'Swagger', 'Sweet Kiss', 'Attract', 'Taunt', 'Torment',
        'Encore', 'Disable', 'Heal Block', 'Embargo', 'Leech Seed',
        
        # Entry hazards
        'Spikes', 'Toxic Spikes', 'Stealth Rock', 'Sticky Web',
        
        # Field effects
        'Trick Room', 'Magic Room', 'Wonder Room', 'Gravity', 'Grassy Terrain',
        'Misty Terrain', 'Electric Terrain', 'Psychic Terrain', 'Rain Dance',
        'Sunny Day', 'Sandstorm', 'Hail', 'Snow', 'Tailwind', 'Light Screen',
        'Reflect', 'Aurora Veil', 'Safeguard', 'Mist',
        
        # Boosting/status moves
        'Swords Dance', 'Dragon Dance', 'Nasty Plot', 'Calm Mind', 'Bulk Up',
        'Agility', 'Rock Polish', 'Quiver Dance', 'Shift Gear', 'Coil',
        'Curse', 'Iron Defense', 'Amnesia', 'Acid Armor', 'Barrier',
        'Cosmic Power', 'Cotton Guard', 'Defend Order', 'Harden', 'Withdraw',
        'Defense Curl', 'Stockpile', 'Charge', 'Focus Energy', 'Meditate',
        'Sharpen', 'Acupressure', 'Howl', 'Work Up', 'Growth', 'Hone Claws',
        'Shell Smash', 'Tail Glow', 'Geomancy', 'No Retreat',
        
        # Recovery moves
        'Recover', 'Roost', 'Slack Off', 'Soft-Boiled', 'Rest', 'Wish',
        'Healing Wish', 'Lunar Dance', 'Heal Order', 'Milk Drink', 'Moonlight',
        'Morning Sun', 'Synthesis', 'Heal Bell', 'Aromatherapy', 'Refresh',
        'Purify', 'Life Dew', 'Shore Up', 'Swallow', 'Strength Sap',
        
        # Protection moves
        'Protect', 'Detect', 'Endure', 'King\'s Shield', 'Spiky Shield',
        'Baneful Bunker', 'Obstruct', 'Silk Trap', 'Burning Bulwark',
        
        # Switching/pivot moves (these don't directly deal KO damage)
        'Teleport', 'Baton Pass', 'Parting Shot', 'Shed Shell',
        
        # Support moves
        'Substitute', 'Helping Hand', 'Follow Me', 'Rage Powder', 'Spotlight',
        'Ally Switch', 'Trick', 'Switcheroo', 'Bestow', 'Instruct',
        'Skill Swap', 'Role Play', 'Entrainment', 'Guard Split', 'Power Split',
        'Speed Swap', 'Guard Swap', 'Power Swap', 'Heart Swap', 'Mimic',
        'Transform', 'Copycat', 'Me First', 'Snatch', 'Recycle', 'Metronome',
        
        # Weather/terrain setters (already listed above but including for clarity)
        
        # Other non-damaging moves
        'Splash', 'Celebrate', 'Hold Hands', 'Happy Hour', 'Conversion',
        'Conversion 2', 'Camouflage', 'Nightmare', 'Perish Song', 'Mean Look',
        'Block', 'Spider Web', 'Sand Tomb', 'Whirlpool', 'Bind', 'Wrap',
        'Fire Spin', 'Magma Storm', 'Infestation', 'Clamp', 'Snore', 'Forest\'s Curse',
        'Trick-or-Treat', 'Rototiller', 'Magnetic Flux', 'Gear Up', 'Electric Terrain',
        'Flower Shield', 'Ion Deluge', 'Powder', 'Tearful Look', 'Baby-Doll Eyes',
        'Play Nice', 'Venom Drench', 'Stockpile', 'Belly Drum', 'Psych Up',
        'Power Trick', 'Guard Split', 'Power Split', 'Speed Swap',
    }
    
    def __init__(self):
        self.tracker = PokemonTracker()
        self.calculator = DamageCalculator()
        self.active_pokemon = {'p1': None, 'p2': None}
        self.last_move = {}
        
    def process_battle_log(self, battle_log: List[Dict]) -> Dict:
        """
        Process a battle log and track all relevant information
        
        Args:
            battle_log: List of parsed battle log entries
            
        Returns:
            Dictionary with battle summary and tracked Pokémon data
        """
        for entry in battle_log:
            self._process_log_entry(entry)
        
        return {
            'pokemon': self.tracker.get_summary(),
            'teams': {
                'p1': [p.name for p in self.tracker.get_team('p1')],
                'p2': [p.name for p in self.tracker.get_team('p2')],
            }
        }
    
    def _process_log_entry(self, entry: Dict):
        """Process a single log entry"""
        cmd_type = entry.get('type')
        args = entry.get('args', [])
        
        if cmd_type == 'player':
            self._handle_player(args)
        elif cmd_type == 'teamsize':
            self._handle_teamsize(args)
        elif cmd_type == 'gametype':
            self._handle_gametype(args)
        elif cmd_type == 'gen':
            self._handle_gen(args)
        elif cmd_type == 'tier':
            self._handle_tier(args)
        elif cmd_type == 'poke':
            self._handle_poke(args)
        elif cmd_type == 'switch' or cmd_type == 'drag':
            self._handle_switch(args)
        elif cmd_type == 'move':
            self._handle_move(args)
        elif cmd_type == '-damage':
            self._handle_damage(args)
        elif cmd_type == 'faint':
            self._handle_faint(args)
        elif cmd_type == '-ability':
            self._handle_ability(args)
        elif cmd_type == '-item':
            self._handle_item(args)
        elif cmd_type == '-enditem':
            self._handle_enditem(args)
        elif cmd_type == '-heal':
            self._handle_heal(args)
    
    def _parse_pokemon_ident(self, ident: str) -> tuple:
        """Parse Pokémon identifier (e.g., 'p1a: Pikachu')"""
        if ':' not in ident:
            return None, None
        parts = ident.split(':', 1)
        position = parts[0].strip()
        name = parts[1].strip()
        player = position[:2]  # p1, p2, etc.
        return f"{player}:{name}", player
    
    def _parse_hp(self, hp_str: str) -> tuple:
        """Parse HP string (e.g., '100/100' or '50/100 psn')"""
        parts = hp_str.split()
        hp_part = parts[0]
        status = parts[1] if len(parts) > 1 else None
        
        if hp_part == '0':
            return 0, 0, status
        
        if '/' in hp_part:
            current, max_hp = hp_part.split('/')
            return int(current), int(max_hp), status
        
        return None, None, status
    
    def _is_attack_move(self, move: str) -> bool:
        """
        Determine if a move is a direct attacking move
        
        Args:
            move: Move name
            
        Returns:
            True if the move is a direct attack, False otherwise
        """
        return move not in self.NON_ATTACK_MOVES
    
    def _handle_player(self, args: List[str]):
        """Handle player command"""
        pass
    
    def _handle_teamsize(self, args: List[str]):
        """Handle team size command"""
        pass
    
    def _handle_gametype(self, args: List[str]):
        """Handle game type command"""
        pass
    
    def _handle_gen(self, args: List[str]):
        """Handle generation command"""
        pass
    
    def _handle_tier(self, args: List[str]):
        """Handle tier command"""
        pass
    
    def _handle_poke(self, args: List[str]):
        """Handle poke command (team preview)"""
        if len(args) >= 2:
            player = args[0]
            species = args[1].split(',')[0]  # Remove gender indicator
            # Register placeholder - will get full details on switch
    
    def _handle_switch(self, args: List[str]):
        """Handle switch/drag command"""
        if len(args) >= 2:
            pokemon_id, player = self._parse_pokemon_ident(args[0])
            details = args[1]
            hp_str = args[2] if len(args) > 2 else ""
            
            if pokemon_id:
                name = pokemon_id.split(':')[1]
                self.tracker.register_pokemon(player, args[0], name, details)
                self.active_pokemon[player] = pokemon_id
                
                if hp_str:
                    hp, max_hp, _ = self._parse_hp(hp_str)
                    if hp is not None and max_hp is not None:
                        self.tracker.track_hp(pokemon_id, hp, max_hp)
    
    def _handle_move(self, args: List[str]):
        """Handle move command"""
        if len(args) >= 2:
            pokemon_id, player = self._parse_pokemon_ident(args[0])
            move = args[1]
            
            if pokemon_id:
                self.tracker.track_move(pokemon_id, move)
                self.last_move[player] = {'pokemon': pokemon_id, 'move': move}
    
    def _handle_damage(self, args: List[str]):
        """Handle damage command"""
        if len(args) >= 2:
            pokemon_id, player = self._parse_pokemon_ident(args[0])
            hp_str = args[1]
            
            if pokemon_id:
                old_hp = self.tracker.get_pokemon(pokemon_id).hp_current if self.tracker.get_pokemon(pokemon_id) else None
                hp, max_hp, _ = self._parse_hp(hp_str)
                
                if hp is not None and max_hp is not None:
                    self.tracker.track_hp(pokemon_id, hp, max_hp)
                    
                    # Calculate damage dealt
                    if old_hp is not None:
                        damage = old_hp - hp
                        # Find the attacker (opponent's last move)
                        opponent = 'p1' if player == 'p2' else 'p2'
                        if opponent in self.last_move:
                            attacker_id = self.last_move[opponent]['pokemon']
                            self.tracker.track_damage(attacker_id, pokemon_id, damage)
    
    def _handle_faint(self, args: List[str]):
        """Handle faint command"""
        if len(args) >= 1:
            pokemon_id, player = self._parse_pokemon_ident(args[0])
            
            if pokemon_id:
                self.tracker.track_faint(pokemon_id)
                
                # Give credit to the attacker
                opponent = 'p1' if player == 'p2' else 'p2'
                if opponent in self.last_move:
                    attacker_id = self.last_move[opponent]['pokemon']
                    move = self.last_move[opponent]['move']
                    
                    # Only attribute kill to move if it's an attacking move
                    if self._is_attack_move(move):
                        self.tracker.track_knockout(attacker_id)
                        self.tracker.track_move_kill(attacker_id, move)
    
    def _handle_ability(self, args: List[str]):
        """Handle ability reveal"""
        if len(args) >= 2:
            pokemon_id, _ = self._parse_pokemon_ident(args[0])
            ability = args[1]
            
            if pokemon_id:
                self.tracker.track_ability(pokemon_id, ability)
    
    def _handle_item(self, args: List[str]):
        """Handle item reveal"""
        if len(args) >= 2:
            pokemon_id, _ = self._parse_pokemon_ident(args[0])
            item = args[1]
            
            if pokemon_id:
                self.tracker.track_item(pokemon_id, item)
    
    def _handle_enditem(self, args: List[str]):
        """Handle item consumption/removal"""
        # Item was used/removed, but we already tracked it being revealed
        pass
    
    def _handle_heal(self, args: List[str]):
        """Handle heal command"""
        if len(args) >= 2:
            pokemon_id, _ = self._parse_pokemon_ident(args[0])
            hp_str = args[1]
            
            if pokemon_id:
                hp, max_hp, _ = self._parse_hp(hp_str)
                if hp is not None and max_hp is not None:
                    self.tracker.track_hp(pokemon_id, hp, max_hp)
    
    def get_tracker(self) -> PokemonTracker:
        """Get the Pokémon tracker"""
        return self.tracker
