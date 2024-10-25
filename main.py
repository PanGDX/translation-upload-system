import os

from utility import add_story
from scrape import scrape
from replace import mass_replace
from upload import upload_to_inkstone, upload_to_patreon
from extract import extract_and_replace_names, get_prompts
from process_story import process_story


if __name__ == '__main__':
    print("""
	Options:
	1. Add story
	2. Process Story
	3. Extract and Replace Names
	4. Scrape Story
	5. Upload Story
	6. Mass Replace
	7. Clear Screen""")
    choice = input(":")

    assert (int(choice))

    match int(choice):
        case 1:
            add_story()
        case 2:
            process_story()
        case 3:
            translation_prompt, reduction_prompt, extraction_prompt = get_prompts()
            extract_and_replace_names(translation_prompt=translation_prompt,
                                      reduction_prompt=reduction_prompt,
                                      extraction_prompt=extraction_prompt)
        case 4:
            scrape()
        case 5:
            upload_to_inkstone
            upload_to_patreon
        case 6:
            mass_replace()
        case 7:
            os.system('cls')
        case _:
            print("Invalid input")
