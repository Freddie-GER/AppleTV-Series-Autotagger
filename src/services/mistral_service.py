import os
from mistralai import Mistral
from ..utils.constants import DEFAULT_MISTRAL_MODEL

class MistralService:
    def __init__(self):
        api_key = os.getenv('MISTRAL_API_KEY')
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        self.client = Mistral(api_key=api_key)
        self.model = DEFAULT_MISTRAL_MODEL

    def parse_filename(self, filename: str) -> dict:
        """
        Parse a filename to extract TV series information using Mistral AI.
        
        Args:
            filename (str): The filename to parse
            
        Returns:
            dict: Contains series_name, season_number, episode_number, episode_title
        """
        messages = [
            {
                "role": "system",
                "content": "You are a TV series filename parser. Extract the series name, season number, episode number, and episode title from filenames. Respond in JSON format."
            },
            {
                "role": "user",
                "content": f"Parse this filename: {filename}\nRespond with JSON containing series_name, season_number, episode_number, and episode_title"
            }
        ]

        response = self.client.chat.complete(
            model=self.model,
            messages=messages
        )

        return response.choices[0].message.content

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