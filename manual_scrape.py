import pyautogui
import pyperclip
import time
import os
from utility import add_story

full_story_name = str(input("Full story name: "))
patreon_story_name = str(input("Patreon Category name: "))
current_chapter_number = int(input("Chapter number: "))
to_chapter = int(input("Until chapter: "))

story_folder = add_story(full_story_name, patreon_story_name)
time.sleep(5)

for counter in range(current_chapter_number, to_chapter + 1):
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'c')

    content = pyperclip.paste()
    with open(os.path.join(os.getcwd(), "inputs", story_folder, f"{counter}.txt"), "w", encoding="utf-8") as file:
        file.write(content)

    pyautogui.press('right')
    time.sleep(2)
