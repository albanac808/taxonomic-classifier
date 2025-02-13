# test_api.py
from api_client import ITISClient
import json
import requests
import sys
from cache_manager import Cache

def check_connectivity():
    try:
        # Try to connect to a reliable service first
        requests.get("https://8.8.8.8", timeout=3)
        # Then try ITIS
        requests.get("https://www.itis.gov", timeout=5)
        return True
    except requests.RequestException as e:
        print(f"Connectivity check failed: {e}")
        print("Please check your internet connection and try again.")
        return False

def test_lookup():
    client = ITISClient()
    
    # First round - all should make API calls
    print("\n--- First Round ---")
    print("Looking up emperor penguin...")
    client.fetch_taxonomy("emperor penguin")
    print("\nLooking up bottlenose dolphin...")
    client.fetch_taxonomy("bottlenose dolphin")
    print("\nLooking up bald eagle...")
    client.fetch_taxonomy("bald eagle")

    # Second round - all should hit cache
    print("\n--- Second Round ---")
    print("Looking up emperor penguin again...")
    client.fetch_taxonomy("emperor penguin")
    print("\nLooking up bottlenose dolphin again...")
    client.fetch_taxonomy("bottlenose dolphin")
    print("\nLooking up bald eagle again...")
    client.fetch_taxonomy("bald eagle")

if __name__ == "__main__":
    test_lookup()