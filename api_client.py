import requests
import time
from typing import Dict, Optional
from collections import OrderedDict
from utils import clean_results

class Cache:
    def __init__(self, max_size=100):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        self.cache[key] = value

class ITISClient:
    def __init__(self):
        self.base_url = "https://www.itis.gov/ITISWebService/jsonservice"
        self.cache = Cache()  #Initialize a new cache
        self.rank_descriptions = {
            "Animalia": "Animals",
            "Chordata": "Animals with spinal cords",
            "Mammalia": "Mammals",
            "Perissodactyla": "Odd-toed ungulates",
            "Equidae": "Horse family",
            "Equus": "Horses, zebras, and donkeys",
            "Felidae": "Cat family",
            "Carnivora": "Meat-eating mammals",
            "Reptilia": "Reptiles",
            "Aves": "Birds",
            "Insecta": "Insects",
            "Equus zebra": "Mountain zebra"
            # We can keep adding more!
        }
    
    def _make_request(self, endpoint: str, params: Dict, max_retries: int = 3) -> Optional[Dict]:
        for attempt in range(max_retries):
            try:
                response = requests.get(endpoint, params=params, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # exponential backoff
                    print(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
        return None

    def _get_tsn_by_common_name(self, common_name: str) -> Optional[int]:
        endpoint = f"{self.base_url}/searchByCommonName"
        params = {"srchKey": common_name.lower()}
        
        data = self._make_request(endpoint, params)
        if not data:
            return None
            
        if data.get("commonNames"):
            for result in data["commonNames"]:
                if result.get("commonName", "").lower() == common_name.lower():
                    return result.get("tsn")
        return None
    
    def _get_tsn_by_common_name(self, common_name: str) -> Optional[int]:
        endpoint = f"{self.base_url}/searchByCommonName"
        params = {"srchKey": common_name.lower()}
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data["commonNames"]:
                print(f"\nNo matches found for '{common_name}'")
                return None
                
            # If we have multiple matches
            if len(data["commonNames"]) > 1:
                # Extract just the common names
                common_names = [match['commonName'] for match in data["commonNames"]]
                # Clean the results
                cleaned_names = clean_results(common_names)
                
                # Create a mapping of cleaned names back to their original data
                name_to_data = {item['commonName']: item for item in data["commonNames"]}
                
                print(f"\nFound multiple matches for '{common_name}':")
                for i, name in enumerate(cleaned_names, 1):
                    print(f"{i}. {name}")
                
                while True:
                    try:
                        choice = input("\nEnter number (or 0 to cancel): ")
                        if not choice.strip():  # Handle empty input
                            return name_to_data[cleaned_names[0]]["tsn"]  # Default to first option
                        choice = int(choice)
                        if choice == 0:
                            return None
                        if 1 <= choice <= len(cleaned_names):
                            selected_name = cleaned_names[choice-1]
                            return name_to_data[selected_name]["tsn"]
                        print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")
            
            return data["commonNames"][0]["tsn"]
            
        except requests.RequestException as e:
            print(f"API Request failed: {e}")
            return None

    def _get_hierarchy_by_tsn(self, tsn: int) -> Optional[Dict]:
        endpoint = f"{self.base_url}/getFullHierarchyFromTSN"
        params = {"tsn": tsn}
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            # Format the response in a more useful way
            if data.get("hierarchyList"):
                hierarchy = {
                    "kingdom": "",
                    "phylum": "",
                    "class": "",
                    "order": "",
                    "family": "",
                    "genus": "",
                    "species": ""
                }

                for entry in data["hierarchyList"]:
                    rank = entry.get("rankName", "").lower()
                    taxon_name = entry.get("taxonName", "")
                    if rank in hierarchy:
                        description = self.rank_descriptions.get(taxon_name, "")
                        hierarchy[rank] = {
                            "name": taxon_name,
                            "description": description
                        }
                return hierarchy
            return None
            
        except requests.RequestException as e:
            print(f"API Request failed: {e}")
            return None

    def fetch_taxonomy(self, common_name: str) -> Optional[Dict]:
        # First, check if we have this in our cache
        cached_result = self.cache.get(common_name.lower())
        if cached_result:
            print("Found in cache!")  # Optional: lets us know we hit the cache
            return cached_result
        
        # If not in cache, do the API calls...
        tsn = self._get_tsn_by_common_name(common_name)
        if not tsn:
            print(f"Could not find TSN for {common_name}")
            return None
            
        # Get the hierarchy and store result in cache before returning
        result = self._get_hierarchy_by_tsn(tsn)
        if result:
            self.cache.set(common_name.lower(), result)
        return result
    
    def _handle_multiple_matches(self, matches):
        print("\nPlease select a number:")
        for i, match in enumerate(matches, 1):
            print(f"{i}. {match['commonName']}")
        
        while True:
            try:
                choice = int(input("Enter number (or 0 to cancel): "))
                if choice == 0:
                    return None
                if 1 <= choice <= len(matches):
                    return matches[choice-1]["tsn"]
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")