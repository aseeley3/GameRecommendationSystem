"""
Tests for the Genre Header Service.
"""

import pytest
from app.services.genre_header_service import GenreHeaderService, create_genre_service


class TestGenreHeaderService:
    
    @pytest.fixture
    def sample_games_data(self):
        return [
            {
                'appid': 1,
                'name': 'Action Game',
                'genres': 'Action;FPS;Multiplayer'
            },
            {
                'appid': 2,
                'name': 'Strategy Game',
                'genres': 'Strategy;RTS;War'
            },
            {
                'appid': 3,
                'name': 'Indie Puzzle',
                'genres': 'Indie;Puzzle;Casual'
            },
            {
                'appid': 4,
                'name': 'Action RPG',
                'genres': 'Action;RPG;Adventure'
            },
            {
                'appid': 5,
                'name': 'No Genre Game',
                'genres': ''
            },
            {
                'appid': 6,
                'name': 'Racing Game',
                'genres': 'Racing;Sports;Simulation'
            }
        ]
    
    @pytest.fixture
    def genre_service(self, sample_games_data):
        """Create a GenreHeaderService instance for testing."""
        return GenreHeaderService(sample_games_data)
    
    def test_get_all_genres(self, genre_service):
        """Test getting all unique genres."""
        genres = genre_service.get_all_genres()
        
        expected_genres = [
            'Action', 'Adventure', 'Casual', 'FPS', 'Indie', 
            'Multiplayer', 'Puzzle', 'RPG', 'RTS', 'Racing', 
            'Simulation', 'Sports', 'Strategy', 'War'
        ]
        
        assert sorted(genres) == sorted(expected_genres)
        assert len(genres) == 14
    
    def test_get_genre_counts(self, genre_service):
        """Test getting genre counts."""
        counts = genre_service.get_genre_counts()
        
        assert counts['Action'] == 2  
        assert counts['Strategy'] == 1  
        assert counts['Indie'] == 1 
        assert counts['Racing'] == 1 
    
    def test_get_popular_genres(self, genre_service):
        """Test getting popular genres."""
        popular = genre_service.get_popular_genres(limit=5)
        
        assert popular[0]['name'] == 'Action'
        assert popular[0]['count'] == 2
        
        # All others should have count of 1
        for genre_info in popular[1:]:
            assert genre_info['count'] == 1
    
    def test_filter_games_by_genre(self, genre_service):
        """Test filtering games by a single genre."""
        action_games = genre_service.filter_games_by_genre('Action')
        assert len(action_games) == 2
        assert action_games[0]['appid'] == 1
        assert action_games[1]['appid'] == 4
        
        strategy_games = genre_service.filter_games_by_genre('Strategy')
        assert len(strategy_games) == 1
        assert strategy_games[0]['appid'] == 2
        
        # Test case insensitive
        action_games_lower = genre_service.filter_games_by_genre('action')
        assert len(action_games_lower) == 2
    
    def test_filter_games_by_genre_all(self, genre_service):
        """Test filtering with 'all' returns all games."""
        all_games = genre_service.filter_games_by_genre('all')
        assert len(all_games) == 6
        
        all_games_empty = genre_service.filter_games_by_genre('')
        assert len(all_games_empty) == 6
    
    def test_filter_games_by_multiple_genres_any(self, genre_service):
        """Test filtering by multiple genres (ANY match)."""
        # Games with Action OR Strategy
        games = genre_service.filter_games_by_multiple_genres(['Action', 'Strategy'], match_all=False)
        assert len(games) == 3  # Games 1, 2, and 4
        
        game_ids = [game['appid'] for game in games]
        assert 1 in game_ids  # Action game
        assert 2 in game_ids  # Strategy game
        assert 4 in game_ids  # Action RPG
    
    def test_filter_games_by_multiple_genres_all(self, genre_service):
        """Test filtering by multiple genres (ALL match)."""
        # Games with both Action AND RPG
        games = genre_service.filter_games_by_multiple_genres(['Action', 'RPG'], match_all=True)
        assert len(games) == 1
        assert games[0]['appid'] == 4  # Action RPG game
        
        # Games with Action AND Strategy (should be none)
        games = genre_service.filter_games_by_multiple_genres(['Action', 'Strategy'], match_all=True)
        assert len(games) == 0
    
    def test_get_genres_for_game(self, genre_service, sample_games_data):
        """Test getting genres for a specific game."""
        action_game = sample_games_data[0]  # Action;FPS;Multiplayer
        genres = genre_service.get_genres_for_game(action_game)
        
        assert genres == ['Action', 'FPS', 'Multiplayer']
        
        no_genre_game = sample_games_data[4]  # Empty genres
        genres = genre_service.get_genres_for_game(no_genre_game)
        assert genres == []
    
    def test_get_genre_statistics(self, genre_service):
        """Test getting genre statistics."""
        stats = genre_service.get_genre_statistics()
        
        assert stats['total_genres'] == 14
        assert stats['total_games'] == 6
        assert stats['games_with_genres'] == 5  # 5 games have genres
        assert stats['games_without_genres'] == 1  # 1 game has no genres
        assert stats['most_popular_genre'] == ('Action', 2)
        assert stats['average_games_per_genre'] > 0
    
    def test_create_genre_service_factory(self, sample_games_data):
        """Test the factory function."""
        service = create_genre_service(sample_games_data)
        assert isinstance(service, GenreHeaderService)
        assert len(service.get_all_genres()) == 14
