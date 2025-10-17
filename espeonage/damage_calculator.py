"""
Damage calculator integration with Smogon's damage-calc
"""

import json
import subprocess
import os
from typing import Dict, Optional, List


class DamageCalculator:
    """
    Interface to Smogon's damage calculator
    Uses Node.js subprocess to call @smogon/calc
    """
    
    def __init__(self):
        self.calc_script = os.path.join(
            os.path.dirname(__file__), 
            '../calc_wrapper.js'
        )
        
    def calculate_damage(
        self,
        attacker: Dict,
        defender: Dict,
        move: str,
        field: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate damage for a move
        
        Args:
            attacker: Attacker Pokémon data (species, level, stats, etc.)
            defender: Defender Pokémon data
            move: Move name
            field: Field conditions (optional)
            
        Returns:
            Dictionary with damage calculation results
        """
        if not os.path.exists(self.calc_script):
            return {
                'error': 'Damage calculator script not found',
                'damage': [0]
            }
        
        # Prepare input data for the calculator
        calc_input = {
            'attacker': attacker,
            'defender': defender,
            'move': move,
            'field': field or {}
        }
        
        try:
            # Call the Node.js wrapper script
            result = subprocess.run(
                ['node', self.calc_script],
                input=json.dumps(calc_input),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {
                    'error': result.stderr,
                    'damage': [0]
                }
        except subprocess.TimeoutExpired:
            return {
                'error': 'Calculator timed out',
                'damage': [0]
            }
        except Exception as e:
            return {
                'error': str(e),
                'damage': [0]
            }
    
    def estimate_stats(
        self,
        species: str,
        level: int,
        observed_hp: Optional[int] = None,
        observed_damage: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Estimate EVs and IVs based on observed damage and HP
        
        Args:
            species: Pokémon species
            level: Pokémon level
            observed_hp: Observed HP value
            observed_damage: List of observed damage calculations
            
        Returns:
            Dictionary with estimated EV spreads
        """
        # This is a placeholder for more complex stat inference
        # Would involve testing different EV combinations and seeing which
        # matches observed damage values
        
        estimates = {
            'species': species,
            'level': level,
            'possible_spreads': []
        }
        
        if observed_hp:
            estimates['observed_hp'] = observed_hp
        
        if observed_damage:
            estimates['observed_damage'] = observed_damage
        
        # TODO: Implement actual EV/IV inference algorithm
        # This would test various EV spreads against observed damage
        
        return estimates
