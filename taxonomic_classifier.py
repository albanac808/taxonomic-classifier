from api_client import ITISClient
from cache_manager import CacheManager

class TaxonomicClassifier:
    def __init__(self):
        self.api_client = ITISClient()
        self.cache = CacheManager()
    
    def get_classification(self, common_name: str) -> dict:
        # Check cache first
        cached_result = self.cache.get(common_name)
        if cached_result:
            return cached_result
            
        # If not in cache, fetch from API
        result = self.api_client.fetch_taxonomy(common_name)
        # Store in cache for future
        self.cache.store(common_name, result)
        return result