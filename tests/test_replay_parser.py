"""Tests for the replay parser module."""

import os
import unittest
from espeonage.replay_parser import ReplayParser


class TestReplayParser(unittest.TestCase):
    """Test cases for ReplayParser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = ReplayParser()
        self.fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    
    def test_parse_replay_html_with_append(self):
        """Test parsing HTML with Replays.append pattern."""
        html_path = os.path.join(self.fixtures_dir, 'replay_append.html')
        with open(html_path, 'r') as f:
            html = f.read()
        
        result = self.parser.parse_replay_html(html)
        
        # Should not return error
        self.assertNotIn('error', result)
        
        # Should have metadata and battle_log
        self.assertIn('metadata', result)
        self.assertIn('battle_log', result)
        
        # Check metadata
        self.assertEqual(result['metadata']['id'], 'gen9ou-2172099392')
        self.assertEqual(result['metadata']['format'], 'gen9ou')
        self.assertEqual(result['metadata']['p1'], 'Player1')
        self.assertEqual(result['metadata']['p2'], 'Player2')
        
        # Check battle_log is not empty
        self.assertGreater(len(result['battle_log']), 0)
        
        # Verify chat lines were filtered out
        for entry in result['battle_log']:
            self.assertNotEqual(entry['type'], 'c')
            self.assertNotEqual(entry['type'], 'chat')
        
        # Verify the log stopped at win command (should be the last entry)
        last_entry = result['battle_log'][-1]
        self.assertEqual(last_entry['type'], 'win')
    
    def test_parse_replay_html_with_embed(self):
        """Test parsing HTML with Replays.embed pattern."""
        html_path = os.path.join(self.fixtures_dir, 'replay_embed.html')
        with open(html_path, 'r') as f:
            html = f.read()
        
        result = self.parser.parse_replay_html(html)
        
        # Should not return error
        self.assertNotIn('error', result)
        
        # Should have metadata and battle_log
        self.assertIn('metadata', result)
        self.assertIn('battle_log', result)
        
        # Check metadata
        self.assertEqual(result['metadata']['id'], 'gen9ou-test123')
        self.assertEqual(result['metadata']['format'], 'gen9ou')
        
        # Check battle_log is not empty
        self.assertGreater(len(result['battle_log']), 0)
    
    def test_parse_replay_file_json(self):
        """Test parsing a JSON replay file."""
        json_path = os.path.join(self.fixtures_dir, 'replay.json')
        
        result = self.parser.parse_replay_file(json_path)
        
        # Should not return error
        self.assertNotIn('error', result)
        
        # Should have metadata and battle_log
        self.assertIn('metadata', result)
        self.assertIn('battle_log', result)
        
        # Check metadata
        self.assertEqual(result['metadata']['id'], 'gen9ou-jsontest')
        self.assertEqual(result['metadata']['p1'], 'JsonPlayer1')
        
        # Check battle_log is not empty
        self.assertGreater(len(result['battle_log']), 0)
    
    def test_parse_replay_file_html(self):
        """Test parsing an HTML replay file."""
        html_path = os.path.join(self.fixtures_dir, 'replay_append.html')
        
        result = self.parser.parse_replay_file(html_path)
        
        # Should not return error
        self.assertNotIn('error', result)
        
        # Should have metadata and battle_log
        self.assertIn('metadata', result)
        self.assertIn('battle_log', result)
        
        # Check battle_log is not empty
        self.assertGreater(len(result['battle_log']), 0)
    
    def test_parse_raw_log(self):
        """Test parsing a raw log string."""
        log = (
            "|player|p1|TestPlayer1|avatar\n"
            "|player|p2|TestPlayer2|avatar\n"
            "|turn|1\n"
            "|switch|p1a: Pikachu|Pikachu, L50|150/150\n"
            "|switch|p2a: Charizard|Charizard, L50|200/200\n"
            "|turn|2\n"
            "|move|p1a: Pikachu|Thunderbolt|p2a: Charizard\n"
            "|-damage|p2a: Charizard|100/200\n"
            "|win|TestPlayer1"
        )
        
        result = self.parser.parse_raw_log(log)
        
        # Should have metadata and battle_log
        self.assertIn('metadata', result)
        self.assertIn('battle_log', result)
        
        # Check battle_log is not empty
        self.assertGreater(len(result['battle_log']), 0)
        
        # Last entry should be win
        last_entry = result['battle_log'][-1]
        self.assertEqual(last_entry['type'], 'win')
    
    def test_chat_filtering(self):
        """Test that chat and UI lines are filtered out."""
        log = (
            "|player|p1|Player1|avatar\n"
            "|c|Player1|hello there\n"
            "|chat|Player2|hi back\n"
            "|html|<div>some html</div>\n"
            "|error|some error\n"
            "|turn|1\n"
            "|switch|p1a: Pikachu|Pikachu, L50|150/150\n"
            "Some random non-pipe text\n"
            "|win|Player1"
        )
        
        result = self.parser.parse_raw_log(log)
        
        # Check that no chat/html/error entries exist
        for entry in result['battle_log']:
            self.assertNotIn(entry['type'], ['c', 'chat', 'html', 'error'])
    
    def test_terminal_command_stops_parsing(self):
        """Test that parsing stops at terminal commands."""
        log = (
            "|player|p1|Player1|avatar\n"
            "|turn|1\n"
            "|switch|p1a: Pikachu|Pikachu, L50|150/150\n"
            "|win|Player1\n"
            "|turn|2\n"
            "|move|p1a: Pikachu|Thunderbolt|p2a: Charizard\n"
        )
        
        result = self.parser.parse_raw_log(log)
        
        # Last command should be win
        last_entry = result['battle_log'][-1]
        self.assertEqual(last_entry['type'], 'win')
        
        # Should not have turn 2 entries
        commands = [entry['type'] for entry in result['battle_log']]
        # Count how many turns we have
        turn_count = commands.count('turn')
        self.assertEqual(turn_count, 1)
    
    def test_tie_terminal_command(self):
        """Test that tie is recognized as a terminal command."""
        log = (
            "|player|p1|Player1|avatar\n"
            "|turn|1\n"
            "|switch|p1a: Pikachu|Pikachu, L50|150/150\n"
            "|tie\n"
            "|turn|2\n"
        )
        
        result = self.parser.parse_raw_log(log)
        
        # Last command should be tie
        last_entry = result['battle_log'][-1]
        self.assertEqual(last_entry['type'], 'tie')
    
    def test_parse_replay_html_no_data(self):
        """Test parsing HTML with no replay data."""
        html = "<html><body>No replay data here</body></html>"
        
        result = self.parser.parse_replay_html(html)
        
        # Should return error
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Could not parse replay data')
    
    def test_parse_log_line_structure(self):
        """Test that log lines are parsed into correct structure."""
        log = "|switch|p1a: Pikachu|Pikachu, L50|150/150\n"
        
        result = self.parser.parse_raw_log(log)
        
        # Check structure of parsed entry
        entry = result['battle_log'][0]
        self.assertIn('type', entry)
        self.assertIn('args', entry)
        self.assertIn('raw', entry)
        
        self.assertEqual(entry['type'], 'switch')
        self.assertEqual(len(entry['args']), 3)
        self.assertEqual(entry['raw'], '|switch|p1a: Pikachu|Pikachu, L50|150/150')


if __name__ == '__main__':
    unittest.main()
