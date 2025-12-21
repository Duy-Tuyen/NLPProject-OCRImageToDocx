import os
import re

# Set the directory path
directory = r"c:\Tuyen\nlp-dataset\Pages in image"

# Get all files in the directory
files = [f for f in os.listdir(directory) if f.endswith('.jpg')]

print(f"Found {len(files)} jpg files")

# Simple pattern to extract just the 4-digit number at the end
pattern = r"-(\d{4})\.jpg$"

# Counter for renamed files
renamed_count = 0

# Iterate through all files
for filename in files:
    match = re.search(pattern, filename)
    if match:
        # Extract the page number
        page_number = match.group(1)
        
        # Create new filename with just the page number (removing leading zeros)
        new_filename = f"{int(page_number)}.jpg"
        
        # Full paths
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_filename)
        
        # Rename the file
        try:
            os.rename(old_path, new_path)
            renamed_count += 1
            print(f"Renamed: {page_number} → {new_filename}")
        except Exception as e:
            print(f"Error renaming {filename}: {e}")
    else:
        print(f"No match for: {filename}")

print(f"\nTotal files renamed: {renamed_count}")
