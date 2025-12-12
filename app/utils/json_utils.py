import json
import os
from typing import Literal, Dict, Any, List

# --- CONFIGURATION ---
DATA_DIR = "data"
FILES = {
    "scraped": os.path.join(DATA_DIR, "scraped.json"),
    "translated": os.path.join(DATA_DIR, "translated.json"),
    "uploaded": os.path.join(DATA_DIR, "uploaded.json")
}


# --- HELPER FUNCTIONS ---

def load_json(filepath: str) -> Dict[str, Any]:
    if not os.path.exists(filepath):
        # Return empty structure if file doesn't exist
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: {filepath} is corrupted. Returning empty dict.")
        return {}

def save_json(filepath: str, data: Dict[str, Any]):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved changes to {filepath}")

# --- MAIN LOGIC FUNCTIONS ---

def edit_chapter_entry(
    file_type: Literal["scraped", "translated", "uploaded"], 
    story_name: str, 
    chapter_num: int, 
    updates: Dict[str, Any]
):
    """
    Edits a specific chapter entry.
    Example: edit_chapter_entry('scraped', 'My Story', 1, {'title': 'New Title'})
    """
    filepath = FILES.get(file_type)
    if not filepath:
        print(f"Invalid file type: {file_type}")
        return

    data = load_json(filepath)

    if story_name not in data:
        print(f"Story '{story_name}' not found in {file_type}.")
        return

    # Find the chapter in the list
    chapters = data[story_name]
    found = False
    
    for chapter in chapters:
        # Assuming structure: {"chapter": 1, "title": "...", ...}
        if chapter.get('chapter') == chapter_num:
            # Update fields
            for key, value in updates.items():
                chapter[key] = value
            found = True
            print(f"Updated Chapter {chapter_num} in {story_name} ({file_type}).")
            break
    
    if not found:
        print(f"Chapter {chapter_num} not found in {story_name}. Creating it...")
        # Optional: Auto-create if not found
        new_entry = {"chapter": chapter_num}
        new_entry.update(updates)
        chapters.append(new_entry)
        # Sort by chapter number to keep it tidy
        data[story_name] = sorted(chapters, key=lambda x: x.get('chapter', 0))

    save_json(filepath, data)


def sync_stories_across_files():
    """
    Ensures that if a Story Name exists in one file, it exists in all files.
    It does NOT sync chapters, just the existence of the Story Key.
    """
    scraped = load_json(FILES['scraped'])
    translated = load_json(FILES['translated'])
    uploaded = load_json(FILES['uploaded'])

    # Get unique set of all story names
    all_stories = set(scraped.keys()) | set(translated.keys()) | set(uploaded.keys())

    datasets = {
        'scraped': scraped,
        'translated': translated,
        'uploaded': uploaded
    }

    changes_made = False

    for story in all_stories:
        for f_type, data in datasets.items():
            if story not in data:
                print(f"Adding missing story key '{story}' to {f_type} file.")
                data[story] = 0 # Initialize as empty list
                changes_made = True

    if changes_made:
        save_json(FILES['scraped'], scraped)
        save_json(FILES['translated'], translated)
        save_json(FILES['uploaded'], uploaded)
        print("Sync complete.")
    else:
        print("All files are already in sync regarding story keys.")


def delete_story_globally(story_name: str, admin=False):
    """
    Removes a story entry from ALL json files.
    """
    print(f"WARNING: About to delete '{story_name}' from all records.")
    confirm = input("Are you sure? (y/n): ")
    
    if not admin and confirm.lower() != 'y':
        print("Operation cancelled.")
        return

    for f_type, path in FILES.items():
        data = load_json(path)
        if story_name in data:
            del data[story_name]
            save_json(path, data)
            print(f"Deleted from {f_type}.")
        else:
            print(f"Story not found in {f_type}, skipping.")


def check_missing_chapters():
    """
    Scans all files and checks for gaps in chapter numbers.
    Assumes chapters start at 1.
    """
    print("\n--- INTEGRITY CHECK ---")
    
    for f_type, path in FILES.items():
        data = load_json(path)
        print(f"\nChecking {f_type.upper()}...")
        
        for story, chapters in data.items():
            if not chapters:
                print(f"  [!] {story}: No chapters found.")
                continue

            # Extract chapter numbers
            existing_nums = sorted([c.get('chapter') for c in chapters if isinstance(c, dict) and 'chapter' in c])
            
            if not existing_nums:
                print(f"  [!] {story}: Entries exist but have no 'chapter' key.")
                continue

            last_chap = existing_nums[-1]
            full_set = set(range(1, last_chap + 1))
            existing_set = set(existing_nums)
            
            missing = sorted(list(full_set - existing_set))

            if missing:
                print(f"  [WARNING] {story}: Missing chapters {missing}")
            else:
                print(f"  [OK] {story}: {len(existing_nums)} chapters (1 to {last_chap})")

# --- INTERACTIVE MENU (For Testing) ---

if __name__ == "__main__":
    # Create dummy files for testing if they don't exist
    if not os.path.exists(FILES['scraped']):
        save_json(FILES['scraped'], {
            "Test Novel": [{"chapter": 1, "title": "Intro"}, {"chapter": 3, "title": "Jump"}]
        })

    while True:
        print("\n=== JSON DATABASE MANAGER ===")
        print("1. Edit Chapter")
        print("2. Sync Stories Keys")
        print("3. Delete Story")
        print("4. Check Missing Chapters")
        print("5. Exit")
        
        choice = input("Select: ")

        if choice == '1':
            f_type = input("File type (scraped/translated/uploaded): ").strip()
            if f_type not in FILES:
                print("Invalid type.")
                continue
            story = input("Story Name: ")
            try:
                chap = int(input("Chapter Number: "))
                key = input("Key to edit (e.g., title, path): ")
                val = input(f"New value for {key}: ")
                edit_chapter_entry(f_type, story, chap, {key: val})
            except ValueError:
                print("Invalid number.")

        elif choice == '2':
            sync_stories_across_files()

        elif choice == '3':
            story = input("Story Name to DELETE: ")
            delete_story_globally(story)

        elif choice == '4':
            check_missing_chapters()

        elif choice == '5':
            break