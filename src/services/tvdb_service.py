import requests
from typing import Dict, List, Optional
from ..utils.constants import TVDB_API_KEY

class TVDBService:
    """Service for interacting with TVDB API V4"""
    
    BASE_URL = "https://api4.thetvdb.com/v4"
    
    def __init__(self):
        self.api_key = TVDB_API_KEY
        self.token = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with TVDB API"""
        response = requests.post(
            f"{self.BASE_URL}/login",
            json={"apikey": self.api_key}
        )
        response.raise_for_status()
        self.token = response.json()["data"]["token"]
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
    
    def search_series(self, query: str) -> List[Dict]:
        """
        Search for TV series by name
        
        Args:
            query: Series name to search for
            
        Returns:
            List of series matches
        """
        response = requests.get(
            f"{self.BASE_URL}/search",
            headers=self._get_headers(),
            params={"query": query, "type": "series"}
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def get_series_details(self, series_id: int) -> Dict:
        """
        Get detailed information about a series
        
        Args:
            series_id: TVDB series ID
            
        Returns:
            Series details including available seasons
        """
        response = requests.get(
            f"{self.BASE_URL}/series/{series_id}/extended",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def get_episode_details(self, episode_id: int) -> Dict:
        """
        Get detailed information about an episode
        
        Args:
            episode_id: TVDB episode ID
            
        Returns:
            Episode details
        """
        response = requests.get(
            f"{self.BASE_URL}/episodes/{episode_id}/extended",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def get_artwork(self, series_id: int, type: Optional[str] = None) -> List[Dict]:
        """
        Get artwork for a series
        
        Args:
            series_id: TVDB series ID
            type: Optional artwork type filter (e.g., 'poster', 'banner')
            
        Returns:
            List of artwork items
        """
        params = {"type": type} if type else {}
        response = requests.get(
            f"{self.BASE_URL}/series/{series_id}/artworks",
            headers=self._get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def get_episodes_by_season(self, series_id: int, season_number: int) -> List[Dict]:
        """
        Get all episodes for a specific season
        
        Args:
            series_id: TVDB series ID
            season_number: Season number
            
        Returns:
            List of episodes in the season
        """
        # First get all seasons to find the season ID
        series_details = self.get_series_details(series_id)
        season_id = None
        
        for season in series_details.get("seasons", []):
            if season.get("number") == season_number:
                season_id = season.get("id")
                break
                
        if not season_id:
            raise ValueError(f"Season {season_number} not found for series {series_id}")
            
        response = requests.get(
            f"{self.BASE_URL}/seasons/{season_id}/extended",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()["data"]["episodes"] 