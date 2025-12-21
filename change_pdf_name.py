"""
Rename PDF files from <text>-<number>.pdf to <number>.pdf
"""

import os
import re


def rename_pdfs(input_folder="input_pdf"):
    """
    Rename all PDFs in folder from pattern '<text>-<number>.pdf' to '<number>.pdf'
    """
    if not os.path.exists(input_folder):
        print(f"Folder '{input_folder}' not found!")
        return
    
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in '{input_folder}'")
        return
    
    renamed_count = 0
    skipped_count = 0
    
    for filename in pdf_files:
        # Extract number after last dash
        match = re.search(r'-(\d+)\.pdf$', filename, re.IGNORECASE)
        
        if match:
            number = match.group(1)
            new_name = f"{number}.pdf"
            
            old_path = os.path.join(input_folder, filename)
            new_path = os.path.join(input_folder, new_name)
            
            if os.path.exists(new_path):
                print(f"Skipped: {filename} (target already exists)")
                skipped_count += 1
            else:
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} → {new_name}")
                renamed_count += 1
        else:
            print(f"Skipped: {filename} (no number pattern found)")
            skipped_count += 1
    
    print(f"\nSummary: {renamed_count} renamed, {skipped_count} skipped")


if __name__ == "__main__":
    rename_pdfs()
