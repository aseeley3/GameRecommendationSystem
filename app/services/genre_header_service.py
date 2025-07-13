from typing import List, Dict, Set, Optional
from collections import Counter


class GenreHeaderService:
    def __init__(self, games_data: List[Dict]):
        self.games_data = games_data
        self._all_genres = None
        self._genre_counts = None
    
    def get_all_genres(self) -> List[str]:
        if self._all_genres is None:
            genres_set = set()
            for game in self.games_data:
                genres_str = game.get('genres', '')
                if genres_str:
                    # Split by semicolon and clean up whitespace
                    game_genres = [genre.strip() for genre in genres_str.split(';') if genre.strip()]
                    genres_set.update(game_genres)
            
            self._all_genres = sorted(list(genres_set))
        
        return self._all_genres
    
    def get_genre_counts(self) -> Dict[str, int]:
        if self._genre_counts is None:
            genre_counter = Counter()
            for game in self.games_data:
                genres_str = game.get('genres', '')
                if genres_str:
                    game_genres = [genre.strip() for genre in genres_str.split(';') if genre.strip()]
                    genre_counter.update(game_genres)
            
            self._genre_counts = dict(genre_counter)
        
        return self._genre_counts
    
    def get_popular_genres(self, limit: int = 20) -> List[Dict[str, any]]:
        genre_counts = self.get_genre_counts()
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'name': genre, 'count': count}
            for genre, count in sorted_genres[:limit]
        ]
    
    def filter_games_by_genre(self, genre: str) -> List[Dict]:
        if not genre or genre.lower() == 'all':
            return self.games_data.copy()
        
        filtered_games = []
        for game in self.games_data:
            genres_str = game.get('genres', '')
            if genres_str:
                game_genres = [g.strip().lower() for g in genres_str.split(';') if g.strip()]
                if genre.lower() in game_genres:
                    filtered_games.append(game)
        
        return filtered_games
    
    def filter_games_by_multiple_genres(self, genres: List[str], match_all: bool = False) -> List[Dict]:
        if not genres:
            return self.games_data.copy()
        
        # Remove 'all' from genres list and normalize to lowercase
        filter_genres = [g.lower() for g in genres if g.lower() != 'all']
        
        if not filter_genres:
            return self.games_data.copy()
        
        filtered_games = []
        for game in self.games_data:
            genres_str = game.get('genres', '')
            if genres_str:
                game_genres = [g.strip().lower() for g in genres_str.split(';') if g.strip()]
                
                if match_all:
                    # Game must have ALL specified genres
                    if all(genre in game_genres for genre in filter_genres):
                        filtered_games.append(game)
                else:
                    # Game must have ANY of the specified genres
                    if any(genre in game_genres for genre in filter_genres):
                        filtered_games.append(game)
        
        return filtered_games
    
    def get_genres_for_game(self, game: Dict) -> List[str]:
        genres_str = game.get('genres', '')
        if not genres_str:
            return []
        
        return [genre.strip() for genre in genres_str.split(';') if genre.strip()]
    
    def get_genre_statistics(self) -> Dict[str, any]:
        genre_counts = self.get_genre_counts()
        all_genres = self.get_all_genres()
        
        total_games = len(self.games_data)
        games_with_genres = sum(1 for game in self.games_data if game.get('genres', '').strip())
        
        return {
            'total_genres': len(all_genres),
            'total_games': total_games,
            'games_with_genres': games_with_genres,
            'games_without_genres': total_games - games_with_genres,
            'most_popular_genre': max(genre_counts.items(), key=lambda x: x[1]) if genre_counts else None,
            'least_popular_genre': min(genre_counts.items(), key=lambda x: x[1]) if genre_counts else None,
            'average_games_per_genre': sum(genre_counts.values()) / len(genre_counts) if genre_counts else 0
        }


# Factory function to create genre service instance
def create_genre_service(games_data: List[Dict]) -> GenreHeaderService:
    return GenreHeaderService(games_data)
