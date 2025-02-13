from api_client import ITISClient
from utils import clean_results

def organize_results(search_results):
    categorized = {
        "MAMMALS": set(),
        "FISH": set(),
        "BIRDS": set(),
        "REPTILES": set(),
        "SNAKES": set(),
        "PLANTS": set(),
        "OTHER": set()
    }
    
    for result in search_results:
        if any(word in result.lower() for word in ["wolf", "canid"]):
            categorized["MAMMALS"].add(result)
        elif any(word in result.lower() for word in ["fish", "eel"]):
            categorized["FISH"].add(result)
        elif "snake" in result.lower():
            categorized["SNAKES"].add(result)
        elif any(word in result.lower() for word in ["berry", "willow", "grass"]):
            categorized["PLANTS"].add(result)
        else:
            categorized["OTHER"].add(result)
            
    return categorized

def display_results(search_term, categorized_results):
    total_count = 0
    print(f"\nFound matches for '{search_term}':")
    
    for category, items in categorized_results.items():
        if items:  # only show categories that have matches
            print(f"\n{category}:")
            for i, item in enumerate(sorted(items), start=total_count + 1):
                print(f"{i}. {item}")
            total_count += len(items)
    
    return total_count

def get_name_priority(name):
    # (previous get_name_priority implementation stays the same)
    name = name.lower()
    score = 0
    
    common_regions = ['north american', 'american', 'european', 'asian', 'african']
    specialist_terms = ['dwarf', 'spotted', 'striped', 'lesser', 'greater', 
                       'eastern', 'western', 'southern', 'northern']
    
    if any(region in name for region in common_regions):
        score += 5
    if 'common' in name:
        score += 10
    if any(term in name for term in specialist_terms):
        score -= 3
    if "'" in name:
        score -= 5
    
    word_count = len(name.split())
    score -= (word_count - 1) * 2
    
    return score

def search_animals():
    client = ITISClient()
    
    while True:
        search = input("\nEnter an animal name (or 'quit' to exit): ").strip()
        
        if search.lower() == 'quit':
            break
            
        print(f"\nSearching for {search}...")
        
        try:
            # Directly fetch taxonomy for the search term
            result = client.fetch_taxonomy(search)
            if result:
                print("\nTaxonomy Results:")
                for rank, info in result.items():
                    if info:
                        name = info.get('name', '')
                        desc = info.get('description', '')
                        if desc:
                            print(f"{rank.title()}: {name} - {desc}")
                        else:
                            print(f"{rank.title()}: {name}")
            else:
                print(f"No results found for '{search}'")
                
        except Exception as e:
            print(f"An error occurred: {e}")
            
        input("\nPress Enter to search again...")

if __name__ == "__main__":
    print("\nWelcome to the Animal Name Search!")
    print("--------------------------------")
    print("This tool helps you search for animal names and shows their taxonomy.")
    print("Type 'quit' at any time to exit.")
    
    search_animals()