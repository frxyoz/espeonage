"""
Pokémon Showdown Replay Parser

This module parses Pokémon Showdown replay pages and raw battle logs.
It supports multiple extraction methods:
- Inline script patterns (Replays.embed, Replays.append, Replays.render)
- JSON-like data blobs in HTML pages
- JSON endpoint fallback (appending .json to replay URLs)
- Raw log file parsing

The parser filters out chat/UI-only content and stops at terminal battle commands.
"""

import re
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional


class ReplayParser:
    """Parser for Pokémon Showdown replay data."""
    
    def __init__(self):
        self.battle_log = []
        self.metadata = {}
    
    def parse_replay_url(self, url: str) -> Dict[str, Any]:
        """
        Parse a Pokémon Showdown replay from a URL.
        
        Attempts to fetch and parse the HTML page, then falls back to 
        the JSON endpoint if HTML parsing fails.
        
        Args:
            url: The replay URL (e.g., https://replay.pokemonshowdown.com/gen9ou-2172099392)
            
        Returns:
            Dict containing parsed replay data with metadata and battle_log,
            or an error dict if parsing fails.
        """
        try:
            # Fetch HTML page
            req = urllib.request.Request(url, headers={'User-Agent': 'Espeonage-ReplayParser/0.1'})
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
            
            # Try to parse HTML
            result = self.parse_replay_html(html, url=url)
            
            # If HTML parsing failed, try JSON endpoint
            if 'error' in result:
                json_url = url.rstrip('/') + '.json'
                try:
                    json_req = urllib.request.Request(json_url, headers={'User-Agent': 'Espeonage-ReplayParser/0.1'})
                    with urllib.request.urlopen(json_req, timeout=10) as json_response:
                        json_data = json.loads(json_response.read().decode('utf-8'))
                    
                    # Check if JSON has valid replay data
                    if json_data and isinstance(json_data, dict):
                        return self.parse_replay_data(json_data)
                except (urllib.error.URLError, json.JSONDecodeError, KeyError):
                    # JSON fallback failed, return original HTML parse error
                    pass
            
            return result
            
        except urllib.error.URLError as e:
            return {"error": f"Failed to fetch URL: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}
    
    def parse_replay_html(self, html: str, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse replay data from HTML content.
        
        Searches for inline script calls (Replays.embed, Replays.append, Replays.render)
        and JSON-like data blobs containing replay information.
        
        Args:
            html: HTML content from a replay page
            url: Optional URL for context/metadata
            
        Returns:
            Dict containing parsed replay data with metadata and battle_log,
            or {"error": "Could not parse replay data"} if parsing fails.
        """
        # Pattern to match various Replays.* function calls with JSON data
        # Matches: Replays.embed(...), Replays.append(...), Replays.render(...)
        patterns = [
            r'Replays\s*\.\s*embed\s*\(\s*({[^}]*(?:{[^}]*}[^}]*)*})\s*\)',
            r'Replays\s*\.\s*append\s*\(\s*({[^}]*(?:{[^}]*}[^}]*)*})\s*\)\s*;?',
            r'Replays\s*\.\s*render\s*\(\s*({[^}]*(?:{[^}]*}[^}]*)*})\s*\)\s*;?',
        ]
        
        replay_data = None
        
        # Try each pattern
        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1)
                    # Clean up JavaScript-style quotes and trailing commas
                    json_str = self._clean_js_json(json_str)
                    replay_data = json.loads(json_str)
                    if replay_data and 'log' in replay_data:
                        break
                except (json.JSONDecodeError, ValueError):
                    continue
        
        # If inline patterns didn't work, try to find JSON blob with "log" key
        if not replay_data:
            # Look for JSON-like structure with a "log" key
            log_pattern = r'({[^{]*"log"\s*:\s*"[^"]*"[^}]*})'
            matches = re.finditer(log_pattern, html, re.DOTALL)
            for match in matches:
                try:
                    json_str = match.group(1)
                    json_str = self._clean_js_json(json_str)
                    potential_data = json.loads(json_str)
                    if potential_data and 'log' in potential_data:
                        replay_data = potential_data
                        break
                except (json.JSONDecodeError, ValueError):
                    continue
        
        if replay_data:
            return self.parse_replay_data(replay_data)
        
        return {"error": "Could not parse replay data"}
    
    def parse_replay_file(self, filepath: str) -> Dict[str, Any]:
        """
        Parse a replay from a local file.
        
        Supports JSON files, HTML files, and raw log files.
        
        Args:
            filepath: Path to the replay file
            
        Returns:
            Dict containing parsed replay data with metadata and battle_log,
            or an error dict if parsing fails.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse as JSON first
            try:
                data = json.loads(content)
                if isinstance(data, dict) and 'log' in data:
                    return self.parse_replay_data(data)
            except json.JSONDecodeError:
                pass
            
            # Check if it looks like HTML
            if '<html' in content.lower() or '<script' in content.lower():
                return self.parse_replay_html(content, url=filepath if filepath.startswith('http') else None)
            
            # Try to parse as raw log
            return self.parse_raw_log(content)
            
        except FileNotFoundError:
            return {"error": f"File not found: {filepath}"}
        except Exception as e:
            return {"error": f"Error reading file: {e}"}
    
    def parse_replay_data(self, replay_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse replay data from a dictionary (typically from JSON).
        
        Extracts metadata and processes the battle log, filtering out chat/UI lines
        and stopping at terminal battle commands.
        
        Args:
            replay_data: Dict containing replay information with 'log' key
            
        Returns:
            Dict with 'metadata' and 'battle_log' keys
        """
        self.battle_log = []
        self.metadata = {}
        
        # Extract metadata
        for key in ['id', 'format', 'p1', 'p2', 'p1id', 'p2id', 'rating', 'uploadtime']:
            if key in replay_data:
                self.metadata[key] = replay_data[key]
        
        # Parse log
        if 'log' in replay_data:
            log_text = replay_data['log']
            self._process_log(log_text)
        
        return {
            'metadata': self.metadata,
            'battle_log': self.battle_log
        }
    
    def parse_raw_log(self, log_text: str) -> Dict[str, Any]:
        """
        Parse a raw battle log (plain text with pipe-separated commands).
        
        Args:
            log_text: Raw log text
            
        Returns:
            Dict with 'metadata' and 'battle_log' keys
        """
        self.battle_log = []
        self.metadata = {}
        self._process_log(log_text)
        
        return {
            'metadata': self.metadata,
            'battle_log': self.battle_log
        }
    
    def _process_log(self, log_text: str) -> None:
        """
        Process battle log text, filtering and parsing each line.
        
        Skips chat/UI lines and stops at terminal battle commands.
        
        Args:
            log_text: The log text to process
        """
        lines = log_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip chat and UI-only lines
            if self._should_skip_line(line):
                continue
            
            # Check if this is a terminal command
            if self._is_terminal_command(line):
                # Parse this final command and then stop
                parsed = self._parse_log_line(line)
                if parsed:
                    self.battle_log.append(parsed)
                break
            
            # Parse the line
            parsed = self._parse_log_line(line)
            if parsed:
                self.battle_log.append(parsed)
    
    def _should_skip_line(self, line: str) -> bool:
        """
        Determine if a line should be skipped (chat/UI only).
        
        Args:
            line: The log line to check
            
        Returns:
            True if the line should be skipped
        """
        # Skip chat and UI lines
        chat_prefixes = ['|c|', '|chat|', '|html|', '|error|']
        for prefix in chat_prefixes:
            if line.startswith(prefix):
                return True
        
        # Skip non-pipe lines that aren't commands
        if not line.startswith('|') and not line.startswith('-'):
            return True
        
        return False
    
    def _is_terminal_command(self, line: str) -> bool:
        """
        Check if a line represents a terminal battle command.
        
        Terminal commands include: win, tie, forcewin
        
        Args:
            line: The log line to check
            
        Returns:
            True if this is a terminal command
        """
        if not line.startswith('|'):
            return False
        
        parts = line.split('|')
        if len(parts) < 2:
            return False
        
        command = parts[1].lstrip('-')
        terminal_commands = ['win', 'tie', 'forcewin']
        
        return command in terminal_commands
    
    def _parse_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single log line into a structured format.
        
        Args:
            line: The log line to parse
            
        Returns:
            Dict with parsed line data, or None if line couldn't be parsed
        """
        if not line.startswith('|'):
            return None
        
        parts = line.split('|')[1:]  # Skip first empty element
        if not parts:
            return None
        
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        return {
            'command': command,
            'args': args,
            'raw': line
        }
    
    def _clean_js_json(self, js_json: str) -> str:
        """
        Clean JavaScript-style JSON to make it valid JSON.
        
        Args:
            js_json: JavaScript-style JSON string
            
        Returns:
            Cleaned JSON string
        """
        # Remove trailing commas before closing braces/brackets
        js_json = re.sub(r',(\s*[}\]])', r'\1', js_json)
        
        # Handle single quotes (convert to double quotes)
        # This is a simplified approach - a full parser would be more robust
        # For now, we'll rely on the JSON being mostly valid
        
        return js_json
