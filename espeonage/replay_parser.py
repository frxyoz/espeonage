"""
Replay parser for Pokémon Showdown replays
"""

import json
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import requests


class ReplayParser:
    """Parser for Pokémon Showdown replay files"""
    
    def __init__(self):
        self.battle_log = []
        self.metadata = {}
        
    def parse_replay_url(self, url: str) -> Dict:
        """
        Parse a Pokémon Showdown replay from a URL
        
        Args:
            url: URL to the replay (e.g., https://replay.pokemonshowdown.com/...)
            
        Returns:
            Dictionary containing parsed replay data
        """
        response = requests.get(url)
        response.raise_for_status()
        
        return self.parse_replay_html(response.text)
    
    def parse_replay_html(self, html: str) -> Dict:
        """
        Parse a Pokémon Showdown replay from HTML content
        
        Args:
            html: HTML content of the replay page
            
        Returns:
            Dictionary containing parsed replay data
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the script tag containing replay data
        script_tags = soup.find_all('script')
        replay_data = None
        
        for script in script_tags:
            if script.string and 'Replays.embed' in script.string:
                # Extract the replay data from the script
                match = re.search(r'Replays\.embed\((.*?)\);', script.string, re.DOTALL)
                if match:
                    try:
                        replay_data = json.loads(match.group(1))
                    except json.JSONDecodeError:
                        pass
                        
        if not replay_data:
            return {"error": "Could not parse replay data"}
            
        return self.parse_replay_data(replay_data)
    
    def parse_replay_data(self, replay_data: Dict) -> Dict:
        """
        Parse structured replay data
        
        Args:
            replay_data: Dictionary containing replay information
            
        Returns:
            Processed replay data with battle log
        """
        log = replay_data.get('log', '')
        
        # Parse the battle log line by line
        self.battle_log = []
        for line in log.split('\n'):
            line = line.strip()
            if line:
                self.battle_log.append(self._parse_log_line(line))
        
        self.metadata = {
            'id': replay_data.get('id', ''),
            'format': replay_data.get('format', ''),
            'players': replay_data.get('players', []),
            'rating': replay_data.get('rating', None),
            'uploadtime': replay_data.get('uploadtime', None)
        }
        
        return {
            'metadata': self.metadata,
            'battle_log': self.battle_log
        }
    
    def parse_replay_file(self, filepath: str) -> Dict:
        """
        Parse a Pokémon Showdown replay from a local file
        
        Args:
            filepath: Path to the replay file
            
        Returns:
            Dictionary containing parsed replay data
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse as JSON first
        try:
            data = json.loads(content)
            return self.parse_replay_data(data)
        except json.JSONDecodeError:
            # Check if it looks like HTML
            if content.strip().startswith('<'):
                return self.parse_replay_html(content)
            else:
                # Treat as raw battle log
                return self.parse_battle_log(content)
    
    def _parse_log_line(self, line: str) -> Dict:
        """
        Parse a single line from the battle log
        
        Args:
            line: Single line from battle log
            
        Returns:
            Dictionary with parsed command and arguments
        """
        if not line.startswith('|'):
            return {'type': 'raw', 'content': line}
        
        parts = line[1:].split('|')
        command = parts[0] if parts else ''
        args = parts[1:] if len(parts) > 1 else []
        
        return {
            'type': command,
            'args': args,
            'raw': line
        }
    
    def get_battle_log(self) -> List[Dict]:
        """Get the parsed battle log"""
        return self.battle_log
    
    def get_metadata(self) -> Dict:
        """Get replay metadata"""
        return self.metadata
    
    def parse_battle_log(self, log: str) -> Dict:
        """
        Parse a raw battle log string
        
        Args:
            log: Raw battle log content
            
        Returns:
            Dictionary containing parsed replay data
        """
        # Parse the battle log line by line
        self.battle_log = []
        for line in log.split('\n'):
            line = line.strip()
            if line:
                self.battle_log.append(self._parse_log_line(line))
        
        self.metadata = {}
        
        return {
            'metadata': self.metadata,
            'battle_log': self.battle_log
        }
