import os
from mistralai import Mistral
from ..utils.constants import DEFAULT_MISTRAL_MODEL
import json
import time
from datetime import datetime, timedelta

class MistralService:
    def __init__(self):
        api_key = os.getenv('MISTRAL_API_KEY')
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        self.client = Mistral(api_key=api_key)
        self.model = DEFAULT_MISTRAL_MODEL
        self.last_request_time = None
        self.min_request_interval = 2.0  # Minimum time between requests in seconds (increased to 2)

    def _wait_for_rate_limit(self):
        """Implement simple rate limiting"""
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def parse_filename(self, filename: str) -> dict:
        """
        Parse a filename to extract TV series information using Mistral AI.
        
        Args:
            filename (str): The filename to parse
            
        Returns:
            dict: Contains series_name, season_number, and episode_number
        """
        messages = [
            {
                "role": "system",
                "content": """You are a TV series filename parser. Extract the series name, season number, and episode number from filenames.
                Follow these rules:
                1. Always respond with valid JSON containing ONLY these fields:
                   - series_name: Clean up the name (remove dots, underscores, quality tags, etc.)
                   - season_number: Extract as integer
                   - episode_number: Extract as integer
                2. Ignore episode titles, release info, quality tags, etc.
                3. Remove any file extensions
                Example inputs and outputs:
                Input: "show.name.s01e02.1080p.web-dl.x264.mp4"
                Output: {"series_name": "Show Name", "season_number": 1, "episode_number": 2}
                
                Input: "Show_Name_1x03_HDTV.mkv"
                Output: {"series_name": "Show Name", "season_number": 1, "episode_number": 3}"""
            },
            {
                "role": "user",
                "content": f"Parse this filename: {filename}"
            }
        ]

        try:
            self._wait_for_rate_limit()
            response = self.client.chat.complete(
                model=self.model,
                messages=messages
            )
            
            content = response.choices[0].message.content.strip()
            try:
                # If the content is already a dictionary, use it directly
                if isinstance(content, dict):
                    parsed = content
                else:
                    # Clean up the content string - remove escaped characters
                    content = content.replace('\\_', '_')  # Replace escaped underscores
                    content = content.replace('\\n', '')   # Remove newlines
                    content = content.replace('\\', '')    # Remove remaining escapes
                    # Try to parse the string as JSON
                    parsed = json.loads(content)
                
                # Validate required fields
                required_fields = ['series_name', 'season_number', 'episode_number']
                for field in required_fields:
                    if field not in parsed:
                        parsed[field] = None
                    elif field in ['season_number', 'episode_number'] and parsed[field] is not None:
                        # Ensure numeric fields are integers
                        parsed[field] = int(parsed[field])
                
                return parsed
            except json.JSONDecodeError:
                print(f"Failed to parse Mistral response as JSON: {content}")
                return {
                    'series_name': None,
                    'season_number': None,
                    'episode_number': None
                }
                
        except Exception as e:
            print(f"Error calling Mistral API: {str(e)}")
            return {
                'series_name': None,
                'season_number': None,
                'episode_number': None
            }

    def enhance_metadata(self, metadata: dict) -> dict:
        """
        Enhance existing metadata with additional details using Mistral AI.
        
        Args:
            metadata (dict): Existing metadata from TVDB
            
        Returns:
            dict: Enhanced metadata
        """
        messages = [
            {
                "role": "system",
                "content": "You are a TV metadata enhancer. Analyze the provided metadata and suggest improvements or additions. Specifically, in the case of a TV Series, make sure Series Descriptions an Episode Descirption are two different things."
            },
            {
                "role": "user",
                "content": f"Enhance this metadata: {metadata}\nProvide additional context, tags, or descriptions if possible."
            }
        ]

        response = self.client.chat.complete(
            model=self.model,
            messages=messages
        )

        return response.choices[0].message.content 