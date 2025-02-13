def clean_results(matches):
    # Convert to lowercase for comparison
    seen = set()
    cleaned = []
    
    # First pass: remove exact duplicates (case-insensitive)
    for match in matches:
        match_lower = match.lower()
        if match_lower not in seen:
            seen.add(match_lower)
            cleaned.append(match)
    
    # Second pass: remove contained duplicates
    final_results = []
    for i, item in enumerate(cleaned):
        is_unique = True
        item_lower = item.lower()
        
        # Skip items that are just plural versions
        if item_lower.endswith('s') and item_lower[:-1] in seen:
            continue
            
        for j, other in enumerate(cleaned):
            if i != j:
                other_lower = other.lower()
                # If this item is contained within another item, skip it
                if item_lower in other_lower and len(item_lower) < len(other_lower):
                    is_unique = False
                    break
        
        if is_unique:
            final_results.append(item)
    
    return final_results