import os
import json
from datetime import datetime
from typing import Set, List, Dict

class FileHandler:
    @staticmethod
    def ensure_directory(directory: str):
        """Create directory if it doesn't exist"""
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    @staticmethod
    def generate_filename(first_name: str, last_name: str, base_dir: str = "wordlists") -> str:
        """Generate a unique filename with timestamp"""
        FileHandler.ensure_directory(base_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_first = "".join(c for c in first_name if c.isalnum())
        safe_last = "".join(c for c in last_name if c.isalnum())
        return os.path.join(base_dir, f"wordlist_{safe_first}_{safe_last}_{timestamp}.txt")
    
    @staticmethod
    def get_recent_wordlists(directory: str = "wordlists", limit: int = 10) -> List[Dict]:
        """Get list of recently created wordlists"""
        if not os.path.exists(directory):
            return []
        
        wordlists = []
        for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                filepath = os.path.join(directory, filename)
                stats = os.stat(filepath)
                wordlists.append({
                    "filename": filename,
                    "path": filepath,
                    "size": stats.st_size,
                    "created": datetime.fromtimestamp(stats.st_ctime),
                    "modified": datetime.fromtimestamp(stats.st_mtime)
                })
        
        # Sort by modification time, newest first
        wordlists.sort(key=lambda x: x["modified"], reverse=True)
        return wordlists[:limit]
    
    @staticmethod
    def get_word_count(filepath: str) -> int:
        """Count words in a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except:
            return 0