import pytest
from app.services.platform_service import PlatformService


class TestPlatformService:
    
    @pytest.fixture
    def sample_games_data(self):
        return [
            {
                'appid': 1,
                'name': 'Windows Only Game',
                'platforms': 'windows'
            },
            {
                'appid': 2,
                'name': 'Cross Platform Game',
                'platforms': 'windows;mac;linux'
            },
            {
                'appid': 3,
                'name': 'Mac Only Game',
                'platforms': 'mac'
            },
            {
                'appid': 4,
                'name': 'Linux Only Game',
                'platforms': 'linux'
            }
        ]
    
    @pytest.fixture
    def platform_service(self, sample_games_data):
        """Create a PlatformService instance for testing."""
        return PlatformService(sample_games_data)
    
    def test_filter_games_by_platform_windows(self, platform_service):
        """Test filtering games for Windows platform."""
        windows_games = platform_service.filter_games_by_platform('windows')
        
        assert len(windows_games) == 2
        game_names = [game['name'] for game in windows_games]
        assert 'Windows Only Game' in game_names
        assert 'Cross Platform Game' in game_names
    
    def test_filter_games_by_platform_mac(self, platform_service):
        """Test filtering games for Mac platform."""
        mac_games = platform_service.filter_games_by_platform('mac')
        
        assert len(mac_games) == 2
        game_names = [game['name'] for game in mac_games]
        assert 'Cross Platform Game' in game_names
        assert 'Mac Only Game' in game_names
    
    def test_filter_games_by_platform_linux(self, platform_service):
        """Test filtering games for Linux platform."""
        linux_games = platform_service.filter_games_by_platform('linux')
        
        assert len(linux_games) == 2
        game_names = [game['name'] for game in linux_games]
        assert 'Cross Platform Game' in game_names
        assert 'Linux Only Game' in game_names
    
    def test_filter_games_by_platform_all(self, platform_service):
        """Test filtering games for all platforms."""
        all_games = platform_service.filter_games_by_platform('all')
        
        assert len(all_games) == 4
    
    def test_get_platforms_for_game(self, platform_service):
        """Test getting platforms for a specific game."""
        cross_platform_game = {
            'appid': 2,
            'name': 'Cross Platform Game',
            'platforms': 'windows;mac;linux'
        }
        
        platforms = platform_service.get_platforms_for_game(cross_platform_game)
        assert set(platforms) == {'Windows', 'Mac', 'Linux'}
    
    def test_get_platform_statistics(self, platform_service):
        """Test getting platform statistics."""
        stats = platform_service.get_platform_statistics()
        
        assert stats['Windows'] == 2
        assert stats['Mac'] == 2
        assert stats['Linux'] == 2
        assert stats['Total'] == 4
