import pyautogui, pyperclip, time, os
from utility import clean_filename, modify_json_file


full_story_name = str(input("Full story name: "))
patreon_story_name = str(input("Patreon Category name: "))
current_chapter_number = int(input("Chapter number: "))

output_folder = clean_filename(full_story_name)
full_dir = os.path.join("inputs", output_folder)
os.makedirs(full_dir, exist_ok=True)

modify_json_file(
	file_path=os.path.join("data.json"),
	append_json={
		full_story_name: {
			"Next Translated Chapter": 1,
			"Next Inkstone Chapter": 1,
			"Next Patreon Chapter": 1,
			"Patreon Category": patreon_story_name
		}
	}
)

time.sleep(5)

for counter in range(current_chapter_number,668):
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'c')
    
    content = pyperclip.paste()
    with open(os.path.join(full_dir,f"{counter}.txt"), "w", encoding="utf-8") as file:
        file.write(content)

    pyautogui.press('right')    
    time.sleep(2)
