import os
from dotenv import load_dotenv
from src.services.mistral_service import MistralService
from src.services.tvdb_service import TVDBService

def test_mistral_connection():
    print("\nTesting Mistral AI connection...")
    try:
        service = MistralService()
        # Test with a simple filename
        result = service.parse_filename("The.Mandalorian.S01E01.Chapter.One.1080p.mkv")
        print("✓ Mistral connection successful")
        print(f"Sample parse result: {result}")
    except Exception as e:
        print(f"✗ Mistral test failed: {str(e)}")

def test_tvdb_connection():
    print("\nTesting TVDB connection...")
    try:
        service = TVDBService()
        # Test with a search query
        results = service.search_series("The Mandalorian")
        print("✓ TVDB connection successful")
        if results:
            print(f"Sample search result: {results[0]['name'] if results else 'No results'}")
    except Exception as e:
        print(f"✗ TVDB test failed: {str(e)}")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    print("Running service tests...")
    test_mistral_connection()
    test_tvdb_connection() 