import json
import re

def parse_age_range(age_str):
    age_str = age_str.lower().strip()
    
    # Special cases
    if age_str in ["mothers", "mother", "family"]:
        return None, None
    if age_str == "all ages":
        return 0, 1200 # Up to 100 years
    
    # Handle "X months+" or "X month+" or "X+ months"
    match = re.search(r'(\d+)\s*month[s]?\s*\+', age_str) or re.search(r'(\d+)\+\s*month[s]?', age_str) or re.search(r'(\d+)\+', age_str)
    if match:
        min_age = int(match.group(1))
        return min_age, 1200 # Setting a large max_age for "plus" ranges
        
    # Handle "X-Y months"
    match = re.search(r'(\d+)\s*-\s*(\d+)\s*month[s]?', age_str)
    if match:
        return int(match.group(1)), int(match.group(2))
        
    # Handle "X-Y years"
    match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*year[s]?', age_str)
    if match:
        return int(float(match.group(1)) * 12), int(float(match.group(2)) * 12)

    # Handle "X year[s]+"
    match = re.search(r'(\d+(?:\.\d+)?)\s*year[s]?\s*\+', age_str)
    if match:
        return int(float(match.group(1)) * 12), 1200

    # Handle weight ranges (X-Ykg) - these are tricky, will map to sensible infant ranges
    match = re.search(r'(\d+)\s*-\s*(\d+)\s*kg', age_str)
    if match:
        # 4-9kg is usually 0-12 months, 5-10kg is 3-12m, 9-15kg is 12-36m etc.
        # For simplicity and given the context of diapers:
        min_kg = int(match.group(1))
        if min_kg < 5: return 0, 12
        if min_kg < 9: return 3, 18
        return 12, 48
    
    # Default/Unparsed
    return 0, 1200

def transform_item(item):
    age_range = item.get("age_range", "")
    min_age, max_age = parse_age_range(age_range)
    
    # Target Customer logic
    target_customer = "baby"
    if age_range.lower() in ["mothers", "mother", "family"]:
        target_customer = "mother"
    
    # Create new item with desired fields
    new_item = {}
    for key, value in item.items():
        if key == "age_range":
            new_item["min_age"] = min_age
            new_item["max_age"] = max_age
            if target_customer == "mother":
                new_item["target_customer"] = "mother"
            else:
                new_item["target_customer"] = "baby"
        else:
            new_item[key] = value
            
    return new_item

def main():
    file_path = "backend/dataset.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    transformed_data = [transform_item(item) for item in data]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(transformed_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
