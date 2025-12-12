import os
import time
import logging
from utility import setup_chrome_driver, clean_file_name, load_json, save_json
from app.utils.automation import BrowserManager

# Setup Logging
logging.basicConfig(
    filename="selenium_driver.log", filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

def get_latest_chapters(bot: BrowserManager, patreon_link: str, inkstone_link: str):
    # 1. Check Inkstone
    bot.driver.get(inkstone_link)
    time.sleep(5) # Wait for load
    ink_text = bot.get_text('inkstone', 'latest_chapter_text')
    # logic: "Chapter 123" -> 123
    inkstone_chap = int(ink_text.split(" ")[-1])

    # 2. Check Patreon
    bot.driver.get(patreon_link)
    time.sleep(5)
    pat_text = bot.get_text('patreon', 'latest_chapter_text')
    # logic: "Story Name - Chapter 123" -> 123
    patreon_chap = int(pat_text.split("- Chapter ")[-1])

    print(f"Detected -> Patreon: {patreon_chap} | Inkstone: {inkstone_chap}")
    return inkstone_chap, patreon_chap

def upload_to_patreon(bot: BrowserManager, category: str, title: str, content: str):
    try:
        print(f"Uploading to Patreon: {title}")
        bot.click('patreon', 'create_button')
        bot.input_text('patreon', 'title_input', title)
        bot.input_text('patreon', 'body_input', content)
        
        # Category Logic
        bot.click('patreon', 'category_dropdown')
        bot.click('patreon', 'category_option_template', dynamic_text=category)
        
        # Publish Flow
        bot.click('patreon', 'next_button')
        bot.click('patreon', 'publish_button')
        bot.click('patreon', 'close_share_dialog')
        time.sleep(2)
    except Exception as e:
        print(f"[Patreon Error] {e}")

def upload_to_inkstone(bot: BrowserManager, title: str, content: str):
    try:
        print(f"Uploading to Inkstone: {title}")
        bot.click('inkstone', 'create_button')
        time.sleep(2)

        # Handle Iframe for Body
        bot.switch_to_frame('inkstone', 'editor_iframe')
        bot.input_text('inkstone', 'body_input_inside_iframe', content)
        bot.switch_to_default()

        # Handle Title and Publish
        bot.input_text('inkstone', 'title_input', title)
        bot.click('inkstone', 'publish_button')
        bot.click('inkstone', 'confirm_button')
        time.sleep(5)
    except Exception as e:
        print(f"[Inkstone Error] {e}")

def process_story_upload(story_name, data, chapters, platform, comments=""):
    driver = setup_chrome_driver()
    bot = BrowserManager(driver) # Initialize our YAML engine
    
    story_dir = clean_file_name(story_name)
    
    # --- INKSTONE LOOP ---
    if platform in ["both", "inkstone"]:
        bot.driver.get(data["Inkstone Link"])
        time.sleep(5)
        current_chap = data["Next Inkstone Chapter"]
        
        for _ in range(chapters):
            file_path = os.path.join(os.getcwd(), "outputs", story_dir, f"{current_chap}.txt")
            if not os.path.exists(file_path):
                print(f"Missing file: {file_path}")
                break
                
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
            
            content = f"For more chapters visit Patreon.\n{raw_text}"
            if comments: content = f"{comments}\n\n{content}"

            upload_to_inkstone(bot, f"Chapter {current_chap}", content)
            current_chap += 1
        
        # Update Data Object (in memory)
        data["Next Inkstone Chapter"] = current_chap

    # --- PATREON LOOP ---
    if platform in ["both", "patreon"]:
        bot.driver.get("https://www.patreon.com/c/FFAddict")
        time.sleep(5)
        current_chap = data["Next Patreon Chapter"]
        
        for _ in range(chapters):
            file_path = os.path.join(os.getcwd(), "outputs", story_dir, f"{current_chap}.txt")
            if not os.path.exists(file_path): break

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            full_title = f"{story_name} - Chapter {current_chap}"
            upload_to_patreon(bot, data["Patreon Category"], full_title, content)
            current_chap += 1
            
        # Update Data Object (in memory)
        data["Next Patreon Chapter"] = current_chap

    driver.quit()
    return data

if __name__ == '__main__':
    json_path = os.path.join(os.getcwd(), 'json', 'data.json')
    story_data = load_json(json_path)
    story_list = list(story_data.keys())

    # User Input UI
    print("\n--- Auto Uploader ---")
    for i, s in enumerate(story_list, 1): print(f"{i}: {s}")
    
    try:
        num_chapters = int(input("Chapters to upload: "))
        p_choice = input("1) Patreon 2) Inkstone 3) Both: ").strip()
        platform_map = {"1": "patreon", "2": "inkstone", "3": "both"}
        platform = platform_map.get(p_choice, "both")
        
        comments = ""
        if platform != "patreon":
            comments = input("Inkstone Comments (optional): ")

        indices = input("Story numbers (space separated): ").split()
        
        # Processing Loop
        for idx in indices:
            i = int(idx) - 1
            if 0 <= i < len(story_list):
                name = story_list[i]
                print(f"\nProcessing: {name}")
                
                # Update Data
                updated_story_data = process_story_upload(name, story_data[name], num_chapters, platform, comments)
                story_data[name] = updated_story_data # Update main dict
                
        # Save State
        save_json(json_path, story_data)
        print("\nAll done. JSON updated.")

    except Exception as e:
        print(f"Critical Error: {e}")