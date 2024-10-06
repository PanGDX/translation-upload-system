# This program handles the mass replacement of names 
# This works for both Chinese and English (input and output) 
# The replacement is read from a json file
# The format of the json file is as follows
# {
#     "story": {
#         "Replace name" : "New name"
#     }
# }

# untested

import re, os
from utility import load_json


def replace_in_all_files(story_folder:str, old_name:str, new_name:str):
    pattern = fr"[ \n,.\-:;\"'!?\[\]]{old_name}[ \n,.\-:;\"'!?\[\]]"
    def replace_with_special_chars(match):
        return f"{match.group(1)}{new_name}{match.group(2)}"
    
    

    # go through each file and replace
    for file in os.listdir(story_folder):
        file_path = os.path.join(story_folder, file)
        file_content = open(file=file_path, mode="r", encoding="utf-8").read()
        with open(file=file_path, mode="w", encoding="utf-8") as file_overwrite:
            overwrite = re.sub(pattern, replace_with_special_chars, file_content)
            file_overwrite.write(overwrite)

replacement_names_json = load_json("Replace.json")
input_folder_question = str(input("Is the story's folder in the 'input' folder? (y/n) "))
if(input_folder_question).lower() == "y":
    isInInputFolder = True
    parent_folder = "input"
else:
    isInInputFolder = False
    parent_folder = "output"

print("Choose the story name using the number")
for i, story in enumerate(os.listdir(os.path.join(parent_folder))):
    print(f"{i}: {story}")

story_folder = os.listdir([int(input(":"))-1])
story_folder = os.path.join( parent_folder, story_folder)


for story, name2name in replacement_names_json.items():
    for old_name, new_name in name2name.items():
        replace_in_all_files(story_folder, old_name, new_name)