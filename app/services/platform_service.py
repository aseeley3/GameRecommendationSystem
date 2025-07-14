import pandas as pd
from typing import List, Dict, Optional


class PlatformService:
    def __init__(self, games_data: List[Dict]):
        # Initialize the platform service with games data
        self.games_data = games_data
    
    def filter_games_by_platform(self, platform: str) -> List[Dict]:
        # platform: e.g., 'windows', 'mac;linux', or 'all'
        if platform == 'all':
            return self.games_data.copy()

        platform_set = set(p.strip().lower() for p in platform.split(';') if p.strip())

        filtered_games = []
        for game in self.games_data:
            platforms_str = game.get('platforms') or game.get('platform')
            if not platforms_str:
                continue
            game_platforms = set(p.strip().lower() for p in platforms_str.split(';'))
            
            # Check if any of the requested platforms are supported by the game
            if platform_set & game_platforms:
                filtered_games.append(game)

        return filtered_games
    
    def _supports_platform(self, game: Dict, platform: str) -> bool:
        # Check if a game supports the specified platform using the 'platforms' column
        platforms_str = game.get('platforms') or game.get('platform')
        if not platforms_str:
            return False
        platforms = [p.strip().lower() for p in platforms_str.split(';')]
        return platform in platforms
    
    def get_platforms_for_game(self, game: Dict) -> List[str]:
        # Get all platforms supported by a game using the 'platforms' column
        platforms_str = game.get('platforms') or game.get('platform')
        if not platforms_str:
            return []
        platforms = [p.strip().capitalize() for p in platforms_str.split(';')]
        return platforms
    
    def get_platform_statistics(self) -> Dict[str, int]:
        # Get statistics about platform support across all games
        stats = {
            'Windows': 0,
            'Mac': 0,
            'Linux': 0,
            'Total': len(self.games_data)
        }
        for game in self.games_data:
            platforms_str = game.get('platforms') or game.get('platform')
            if not platforms_str:
                continue
            platforms = [p.strip().lower() for p in platforms_str.split(';')]
            if 'windows' in platforms:
                stats['Windows'] += 1
            if 'mac' in platforms:
                stats['Mac'] += 1
            if 'linux' in platforms:
                stats['Linux'] += 1
        return stats
    
    
# Factory function to create platform service instance
def create_platform_service(games_data: List[Dict]) -> PlatformService:
    return PlatformService(games_data) 