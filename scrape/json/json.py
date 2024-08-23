#######################################################################################################################
# JSON utils function
#######################################################################################################################
import json
import os
import time

def read_json(file_path):
    """Read JSON data from a file."""
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return None
    
    with open(file_path, 'r') as file:
        try:
            data = json.load(file)
            return data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

def write_json(data, base_filename):
    """Write JSON data to a file with a timestamp in the filename."""
    if not isinstance(data, dict):
        print("Data must be a dictionary.")
        return
    
    data['timestamp'] = time.time()
    filename = f"{base_filename}"
    
    with open(filename, 'w') as file:
        try:
            json.dump(data, file, indent=4)
        except (TypeError, ValueError) as e:
            print(f"Error writing JSON: {e}")