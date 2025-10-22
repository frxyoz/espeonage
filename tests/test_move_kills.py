"""Tests for move kill tracking functionality."""

import unittest
from espeonage.battle_simulator import BattleSimulator
from espeonage.replay_parser import ReplayParser


class TestMoveKills(unittest.TestCase):
    """Test cases for move kill tracking."""
    
    def test_attack_move_classification(self):
        """Test that attack moves are correctly identified."""
        simulator = BattleSimulator()
        
        # Test attacking moves
        self.assertTrue(simulator._is_attack_move('Earthquake'))
        self.assertTrue(simulator._is_attack_move('Thunderbolt'))
        self.assertTrue(simulator._is_attack_move('Hydro Pump'))
        self.assertTrue(simulator._is_attack_move('Flamethrower'))
        self.assertTrue(simulator._is_attack_move('Ice Beam'))
        self.assertTrue(simulator._is_attack_move('Dragon Claw'))
        
        # Test non-attacking moves
        self.assertFalse(simulator._is_attack_move('Stealth Rock'))
        self.assertFalse(simulator._is_attack_move('Toxic'))
        self.assertFalse(simulator._is_attack_move('Recover'))
        self.assertFalse(simulator._is_attack_move('Swords Dance'))
        self.assertFalse(simulator._is_attack_move('Will-O-Wisp'))
        self.assertFalse(simulator._is_attack_move('Thunder Wave'))
        self.assertFalse(simulator._is_attack_move('Leech Seed'))
        self.assertFalse(simulator._is_attack_move('Spikes'))
    
    def test_move_kills_tracked_for_attacks(self):
        """Test that kills are tracked for direct attacking moves."""
        parser = ReplayParser()
        log = (
            "|player|p1|Player1|\n"
            "|player|p2|Player2|\n"
            "|switch|p1a: Pikachu|Pikachu, L50|150/150\n"
            "|switch|p2a: Charizard|Charizard, L50|200/200\n"
            "|turn|1\n"
            "|move|p1a: Pikachu|Thunderbolt|p2a: Charizard\n"
            "|-damage|p2a: Charizard|0 fnt\n"
            "|faint|p2a: Charizard\n"
            "|win|Player1\n"
        )
        
        result = parser.parse_raw_log(log)
        simulator = BattleSimulator()
        battle_result = simulator.process_battle_log(result['battle_log'])
        
        pikachu_data = battle_result['pokemon']['p1:Pikachu']
        
        # Pikachu should have 1 knockout
        self.assertEqual(pikachu_data['knockouts'], 1)
        
        # Pikachu should have 1 kill with Thunderbolt
        self.assertIn('Thunderbolt', pikachu_data['move_kills'])
        self.assertEqual(pikachu_data['move_kills']['Thunderbolt'], 1)
    
    def test_move_kills_not_tracked_for_status(self):
        """Test that kills from status effects are not tracked."""
        parser = ReplayParser()
        log = (
            "|player|p1|Player1|\n"
            "|player|p2|Player2|\n"
            "|switch|p1a: Toxapex|Toxapex, L50|150/150\n"
            "|switch|p2a: Charizard|Charizard, L50|200/200\n"
            "|turn|1\n"
            "|move|p1a: Toxapex|Toxic|p2a: Charizard\n"
            "|-status|p2a: Charizard|tox\n"
            "|move|p2a: Charizard|Flamethrower|p1a: Toxapex\n"
            "|-damage|p1a: Toxapex|100/150\n"
            "|turn|2\n"
            "|move|p1a: Toxapex|Recover|p1a: Toxapex\n"
            "|-heal|p1a: Toxapex|150/150\n"
            "|move|p2a: Charizard|Flamethrower|p1a: Toxapex\n"
            "|-damage|p1a: Toxapex|100/150\n"
            "|-damage|p2a: Charizard|180/200 tox|[from] psn\n"
            "|turn|3\n"
            "|move|p1a: Toxapex|Recover|p1a: Toxapex\n"
            "|-heal|p1a: Toxapex|150/150\n"
            "|-damage|p2a: Charizard|0 fnt|[from] psn\n"
            "|faint|p2a: Charizard\n"
            "|win|Player1\n"
        )
        
        result = parser.parse_raw_log(log)
        simulator = BattleSimulator()
        battle_result = simulator.process_battle_log(result['battle_log'])
        
        toxapex_data = battle_result['pokemon']['p1:Toxapex']
        
        # Toxapex should have 0 knockouts because the kill was from status
        # (Recover was the last move used, which is non-attacking)
        self.assertEqual(toxapex_data['knockouts'], 0)
        
        # Toxapex should have no move kills
        self.assertEqual(len(toxapex_data['move_kills']), 0)
    
    def test_multiple_kills_same_move(self):
        """Test that multiple kills with the same move are tracked correctly."""
        parser = ReplayParser()
        log = (
            "|player|p1|Player1|\n"
            "|player|p2|Player2|\n"
            "|switch|p1a: Pikachu|Pikachu, L50|150/150\n"
            "|switch|p2a: Charizard|Charizard, L50|200/200\n"
            "|turn|1\n"
            "|move|p1a: Pikachu|Thunderbolt|p2a: Charizard\n"
            "|-damage|p2a: Charizard|0 fnt\n"
            "|faint|p2a: Charizard\n"
            "|switch|p2a: Blastoise|Blastoise, L50|180/180\n"
            "|turn|2\n"
            "|move|p1a: Pikachu|Thunderbolt|p2a: Blastoise\n"
            "|-damage|p2a: Blastoise|0 fnt\n"
            "|faint|p2a: Blastoise\n"
            "|win|Player1\n"
        )
        
        result = parser.parse_raw_log(log)
        simulator = BattleSimulator()
        battle_result = simulator.process_battle_log(result['battle_log'])
        
        pikachu_data = battle_result['pokemon']['p1:Pikachu']
        
        # Pikachu should have 2 knockouts
        self.assertEqual(pikachu_data['knockouts'], 2)
        
        # Pikachu should have 2 kills with Thunderbolt
        self.assertIn('Thunderbolt', pikachu_data['move_kills'])
        self.assertEqual(pikachu_data['move_kills']['Thunderbolt'], 2)
    
    def test_multiple_kills_different_moves(self):
        """Test that kills from different moves are tracked separately."""
        parser = ReplayParser()
        log = (
            "|player|p1|Player1|\n"
            "|player|p2|Player2|\n"
            "|switch|p1a: Pikachu|Pikachu, L50|150/150\n"
            "|switch|p2a: Charizard|Charizard, L50|200/200\n"
            "|turn|1\n"
            "|move|p1a: Pikachu|Thunderbolt|p2a: Charizard\n"
            "|-damage|p2a: Charizard|0 fnt\n"
            "|faint|p2a: Charizard\n"
            "|switch|p2a: Pidgeot|Pidgeot, L50|160/160\n"
            "|turn|2\n"
            "|move|p1a: Pikachu|Iron Tail|p2a: Pidgeot\n"
            "|-damage|p2a: Pidgeot|0 fnt\n"
            "|faint|p2a: Pidgeot\n"
            "|win|Player1\n"
        )
        
        result = parser.parse_raw_log(log)
        simulator = BattleSimulator()
        battle_result = simulator.process_battle_log(result['battle_log'])
        
        pikachu_data = battle_result['pokemon']['p1:Pikachu']
        
        # Pikachu should have 2 knockouts
        self.assertEqual(pikachu_data['knockouts'], 2)
        
        # Pikachu should have 1 kill with Thunderbolt
        self.assertIn('Thunderbolt', pikachu_data['move_kills'])
        self.assertEqual(pikachu_data['move_kills']['Thunderbolt'], 1)
        
        # Pikachu should have 1 kill with Iron Tail
        self.assertIn('Iron Tail', pikachu_data['move_kills'])
        self.assertEqual(pikachu_data['move_kills']['Iron Tail'], 1)
    
    def test_hazard_kill_not_attributed(self):
        """Test that kills from hazards like Stealth Rock are not attributed."""
        parser = ReplayParser()
        log = (
            "|player|p1|Player1|\n"
            "|player|p2|Player2|\n"
            "|switch|p1a: Ferrothorn|Ferrothorn, L50|150/150\n"
            "|switch|p2a: Charizard|Charizard, L50|200/200\n"
            "|turn|1\n"
            "|move|p1a: Ferrothorn|Stealth Rock|p2a: Charizard\n"
            "|-sidestart|p2: Player2|move: Stealth Rock\n"
            "|move|p2a: Charizard|Fire Blast|p1a: Ferrothorn\n"
            "|-damage|p1a: Ferrothorn|100/150\n"
            "|turn|2\n"
            "|switch|p2a: Moltres|Moltres, L50|180/180\n"
            "|-damage|p2a: Moltres|0 fnt|[from] Stealth Rock\n"
            "|faint|p2a: Moltres\n"
            "|win|Player1\n"
        )
        
        result = parser.parse_raw_log(log)
        simulator = BattleSimulator()
        battle_result = simulator.process_battle_log(result['battle_log'])
        
        ferrothorn_data = battle_result['pokemon']['p1:Ferrothorn']
        
        # Ferrothorn should have 0 knockouts (hazard kills don't count)
        self.assertEqual(ferrothorn_data['knockouts'], 0)
        
        # Ferrothorn should have no move kills
        self.assertEqual(len(ferrothorn_data['move_kills']), 0)


if __name__ == '__main__':
    unittest.main()
