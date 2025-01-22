from typing import List, Dict
from pathlib import Path
import json
from mutagen.mp4 import MP4, MP4Cover
import requests
from io import BytesIO
from datetime import datetime
from tqdm import tqdm

from .mistral_service import MistralService
from .tvdb_service import TVDBService

class FileProcessor:
    def __init__(self):
        self.mistral = MistralService()
        self.tvdb = TVDBService()
    
    def analyze_files(self, file_paths: List[str]) -> List[Dict]:
        """
        First pass: Analyze files and get metadata suggestions
        Returns list of dicts with file info and suggested metadata
        """
        results = []
        
        # Create progress bar
        pbar = tqdm(total=len(file_paths), desc="Processing files", unit="file")
        
        for file_path in file_paths:
            try:
                filename = Path(file_path).name
                pbar.set_description(f"Processing {filename}")
                
                # Get initial parse from Mistral
                parsed_info = self.mistral.parse_filename(filename)
                
                # Initialize result dictionary
                result = {
                    'file_path': file_path,
                    'filename': filename,
                    'parsed_info': parsed_info,
                    'series_info': None,
                    'episode_info': None
                }
                
                # Only proceed with TVDB search if we have a valid series name
                if parsed_info and parsed_info.get('series_name'):
                    try:
                        # Search TVDB for the series
                        series_results = self.tvdb.search_series(parsed_info['series_name'])
                        
                        if series_results:
                            series = series_results[0]  # Take best match
                            series_id = series['id']
                            # Clean up series ID if needed
                            if isinstance(series_id, str) and series_id.startswith('series-'):
                                series_id = int(series_id.replace('series-', ''))
                            
                            # Get series details
                            series_details = self.tvdb.get_series_details(series_id)
                            result['series_info'] = series_details
                            
                            # Get episode details if we have season/episode numbers
                            if parsed_info.get('season_number') is not None and parsed_info.get('episode_number') is not None:
                                try:
                                    episodes = self.tvdb.get_episodes_by_season(
                                        series_id,  # Use cleaned series_id
                                        parsed_info['season_number']
                                    )
                                    # Find matching episode
                                    for episode in episodes:
                                        if episode.get('number') == parsed_info['episode_number']:
                                            result['episode_info'] = episode
                                            break
                                except Exception as e:
                                    print(f"Error getting episode details: {str(e)}")
                    except Exception as e:
                        print(f"Error searching TVDB: {str(e)}")
                
                results.append(result)
                pbar.update(1)
                
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                results.append({
                    'file_path': file_path,
                    'filename': Path(file_path).name,
                    'error': str(e),
                    'parsed_info': None,
                    'series_info': None,
                    'episode_info': None
                })
                pbar.update(1)
        
        pbar.close()
        return results
    
    def apply_tags(self, metadata: Dict, language: str = 'eng') -> bool:
        """
        Apply the metadata tags to the file
        Returns True if successful
        """
        try:
            file_path = metadata['file_path']
            video = MP4(file_path)
            
            # Basic metadata
            video['\xa9nam'] = metadata['episode_title']  # Title
            video['tvsh'] = metadata['series_name']      # Show Name
            video['\xa9alb'] = metadata['series_name']   # Album (show name)
            
            # Season and episode numbers
            try:
                season_num = int(metadata['season_number'])
                episode_num = int(metadata['episode_number'])
                video['tvsn'] = [season_num]   # Season number
                video['tves'] = [episode_num]  # Episode number
                
                # Track number (episode) and total (season episodes)
                video['trkn'] = [(episode_num, 0)]  # Second number is total episodes (optional)
                
                # Disk number (season) and total (total seasons)
                video['disk'] = [(season_num, 0)]  # Second number is total seasons (optional)
            except (ValueError, TypeError):
                pass
            
            # Media type and content rating
            video['stik'] = [10]  # 10 = TV Show
            if metadata['series_info'] and metadata['series_info'].get('rating'):
                video['rtng'] = [self._convert_rating(metadata['series_info']['rating'])]
            
            # Additional metadata from TVDB
            if metadata['series_info']:
                # Genre
                if metadata['series_info'].get('genre'):
                    video['\xa9gen'] = metadata['series_info']['genre'][0] if isinstance(metadata['series_info']['genre'], list) else metadata['series_info']['genre']
                
                # Release date
                if metadata['episode_info'] and metadata['episode_info'].get('aired'):
                    try:
                        air_date = datetime.strptime(metadata['episode_info']['aired'], '%Y-%m-%d')
                        video['\xa9day'] = air_date.strftime('%Y-%m-%d')
                    except (ValueError, TypeError):
                        pass
                
                # Long description (series + episode)
                series_desc = metadata['series_info'].get('overview', '')
                episode_desc = metadata['episode_info'].get('overview', '') if metadata['episode_info'] else ''
                
                if episode_desc:
                    video['desc'] = episode_desc
                if series_desc:
                    video['ldes'] = series_desc
            
            # Save changes
            video.save()
            return True
            
        except Exception as e:
            print(f"Error applying tags: {str(e)}")
            return False
    
    def _convert_rating(self, rating: str) -> int:
        """Convert content rating to iTunes rating number"""
        # US TV Ratings
        ratings_map = {
            'TV-Y': 100,
            'TV-Y7': 200,
            'TV-G': 300,
            'TV-PG': 400,
            'TV-14': 500,
            'TV-MA': 600,
            # Add more mappings as needed
        }
        return ratings_map.get(rating, 0)
    
    def apply_tags_to_files(self, metadata_list: List[Dict], language: str = 'eng') -> List[bool]:
        """
        Apply tags to multiple files with progress tracking
        
        Args:
            metadata_list: List of metadata dictionaries for each file
            language: Language code for metadata
            
        Returns:
            List of booleans indicating success/failure for each file
        """
        results = []
        pbar = tqdm(total=len(metadata_list), desc="Applying tags", unit="file")
        
        for metadata in metadata_list:
            try:
                filename = Path(metadata['file_path']).name
                pbar.set_description(f"Tagging {filename}")
                
                success = self.apply_tags(metadata, language)
                results.append(success)
                
            except Exception as e:
                print(f"Error applying tags to {metadata.get('file_path')}: {str(e)}")
                results.append(False)
            
            pbar.update(1)
        
        pbar.close()
        return results 