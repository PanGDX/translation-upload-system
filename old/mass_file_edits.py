"""
Status: Working

This program is a collection of functions that are useful in managing the stories and common issues that arise.
"""

# Test Status: Tested

import re, os, filecmp, json
from old.utility import load_json

def mass_replace():
    def replace_in_all_files(story_folder: str, old_name: str, new_name: str):
        # Adding capturing groups around the special characters

        pattern = fr"(?<![A-Za-z]){old_name}(?![A-Za-z])"        
        for file in os.listdir(story_folder):
            file_path = os.path.join(story_folder, file)
            file_content = open(file=file_path, mode="r", encoding="utf-8").read()
            with open(file=file_path, mode="w", encoding="utf-8") as file_overwrite:
                overwrite = re.sub(
                    pattern,
                    new_name,
                    file_content
                )
                file_overwrite.write(overwrite)

    replacement_names_json = load_json(os.path.join(os.getcwd(),'json','name2name.json'))

    for story_dir, name2name in replacement_names_json.items():
        for new_name, old_name_list in name2name.items():
            for old_name in old_name_list:
                print(f"Replacing: {old_name} -> {new_name}")
                replace_in_all_files(story_dir, old_name, new_name)

def replace_in_all_files(story_folder: str, old_name: str, new_name: str):
    # Adding capturing groups around the special characters

    pattern = fr"(?<![A-Za-z]){old_name}(?![A-Za-z])"        
    for file in os.listdir(story_folder):
        file_path = os.path.join(story_folder, file)
        file_content = open(file=file_path, mode="r", encoding="utf-8").read()
        with open(file=file_path, mode="w", encoding="utf-8") as file_overwrite:
            overwrite = re.sub(
                pattern,
                new_name,
                file_content
            )
            file_overwrite.write(overwrite)

def cut_front_and_back():
    """
    ### @param front_cut: the number of lines to be removed in front. Inclusive.
    ### @param back_cut: the number of lines to be removed at the back. Inclusive. 
    """
    story_folder = choose_file_dir()

    front_cut = int(input("Front cut: "))
    back_cut = int(input("Back cut: "))

    for name in os.listdir(story_folder):
        with open(os.path.join(story_folder, name), "r", encoding='utf-8') as file:
            content = file.readlines()

        content = content[front_cut:-back_cut]
        content = "".join(content)
        with open(os.path.join(story_folder, name), "w", encoding='utf-8') as file:
            file.write(content)
        print(f"Done: {name}")


def remove_all_name_paddings():
    """
    Removes all the paddings in the names of all stories. O(N)
    For example: 0001.txt -> 1.txt
    """
    parent_folder = os.path.join(os.getcwd(), "inputs")
    for story in os.listdir(parent_folder):
        story_folder = os.path.join(parent_folder, story)
        for chapter in os.listdir(story_folder):
            if(chapter[0] == '0'):
                os.rename(
                    src = os.path.join(story_folder, chapter),
                    dst = os.path.join(story_folder, chapter.lstrip("0"))
                )
                print(f"Renamed: {chapter} -> {chapter.lstrip('0')}")

def check_sequential_file_number():
    """
    Checks that all chapters exist in sequential numbers
    Optional: Edit
    """
    parent_folder = os.path.join(os.getcwd(), "inputs")
    for story in os.listdir(parent_folder):
        story_folder = os.path.join(parent_folder, story)
        for counter, chapter in enumerate(os.listdir(story_folder),1):
            if(int(chapter.split('.')[0]) != counter):
                print(f"Error: {counter} != {chapter} for story: {story}")
                break

def check_sequential_file_number():
    """
    Checks that all chapters exist in sequential numbers
    Optional: Edit
    """
    for folder in ["inputs", "outputs"]:
        parent_folder = os.path.join(os.getcwd(), folder)
        for story in os.listdir(parent_folder):
            story_folder = os.path.join(parent_folder, story)
            files = os.listdir(story_folder)

            txt_files = [f for f in files if f.endswith('.txt')]
            sorted_files = sorted(txt_files, key=lambda x: int(x.split('.')[0]))
            
            for counter, chapter in enumerate(sorted_files, int(sorted_files[0].split(".")[0])):
                if(int(chapter.split('.')[0]) != counter):
                    print(f"Error: {counter} != {chapter} for story: {story}")
                    break

def make_sequential_file_number():

    for folder in ["inputs", "outputs"]:
        parent_folder = os.path.join(os.getcwd(), folder)
        for story in os.listdir(parent_folder):
            story_folder = os.path.join(parent_folder, story)
            files = os.listdir(story_folder)

            txt_files = [f for f in files if f.endswith('.txt')]
            sorted_files = sorted(txt_files, key=lambda x: int(x.split('.')[0]))
            
            print()
            print("#######################################")
            print(f"Editing in: {story_folder}")
            for counter, chapter in enumerate(sorted_files,int(sorted_files[0].split(".")[0])):
                os.rename(
                src = os.path.join(story_folder, chapter),
                dst = os.path.join(story_folder, f"{counter}.txt")
                )
                print(f"{chapter} -> {counter}.txt")


def check_and_remove_duplicates(directory):
    # Get all .txt files sorted by name
    files = sorted([f for f in os.listdir(directory) if f.endswith('.txt')])
    
    remove_files = []
    for i in range(len(files) - 1):
        file1 = os.path.join(directory, files[i])
        file2 = os.path.join(directory, files[i+1])
        
        # Compare the two consecutive files
        if filecmp.cmp(file1, file2, shallow=False):  # shallow=False compares file content
            remove_files.append(file2)

    for file in remove_files:
        os.remove(file)  # Remove the repeated file
        print("Removed: " + file)

def check_duplicates():
    folders = filter(os.path.isdir, os.listdir(os.path.join(os.getcwd(), "inputs")))
    for folder in folders:
        directory = os.path.join(os.getcwd(), "inputs", folder)
        files = sorted([f for f in os.listdir(directory) if f.endswith('.txt')])
    
        for i in range(len(files) - 1):
            file1 = os.path.join(directory, files[i])
            file2 = os.path.join(directory, files[i+1])
        
        if filecmp.cmp(file1, file2, shallow=False):  # shallow=False compares file content
            print(f"Same file: {file1} & {file2}")


def modify_name2name_json_file(full_story_dir_list: str|list, old_name: str, new_name: str):
    """
    ### @param full_story_name
    ### @param old_name: old name to be replaced
    ### @param new_name: new name to use to replace
    Add a new name to do replace old_name with.


    name2name.json has the format:
    {
        "story dir":
            {
                "new_name" : ["old1", "old2"]
            }
    }
    """
    if full_story_dir_list == 'str':
        full_story_dir_list = [full_story_dir_list]
    for full_story_dir in full_story_dir_list:
        file_path = os.path.join(os.getcwd(), "json", "name2name.json")
        with open(file_path, 'r') as file:
            data = json.load(file)

        if full_story_dir not in data:
            data[full_story_dir] = {}

        if (new_name not in data[full_story_dir]):
            data[full_story_dir][new_name] = []

        assert (type(data[full_story_dir][new_name]) == list)
        data[full_story_dir][new_name].append(old_name)

        json_object = json.dumps(data, indent=4)
        name2name_dir = os.path.join(os.getcwd(), 'json', 'name2name.json')
        with open(name2name_dir, "w") as outfile:
            outfile.write(json_object)

def choose_file_dir(is_input_folder:bool = True):
    if not is_input_folder:
        parent_folder = os.path.join(os.getcwd(), "outputs")
    else:
        parent_folder = os.path.join(os.getcwd(), "inputs")
    print("Choose the story name using the number")
    for i, story in enumerate(os.listdir(parent_folder)):
        print(f"{i+1}: {story}")

    story_folder = os.listdir(parent_folder)[int(input(":"))-1]
    story_folder = os.path.join(parent_folder, story_folder)

    return story_folder


if __name__ == '__main__':
    while True:
        print("1. Mass Replace Names using name2name.json")
        print("2. Modify name2name json")
        print("3. Cut Front and Back")
        print("4. Remove all name paddings")
        print("5. Check that files are sequential")
        print("6. Make all files sequential")
        print("7. Check and remove all file duplicates")
        print("8. Check Duplicates")
        print("9. Mass replace one-off")
        choice = int(input("Choice: "))
        match choice:
            case 1:
                mass_replace()
            case 2:
                is_input_folder = input('Input Folder? (y/n/b): ').lower().strip()
                old_name = str(input("Old name:"))
                new_name = str(input("New name:"))
                
                match is_input_folder:
                    case 'y':
                        folder_dir = choose_file_dir(True)
                    case 'n':
                        folder_dir = choose_file_dir(False)
                    case 'b':
                        folder_dir = [choose_file_dir(True)]
                        folder_dir.append(folder_dir[0].replace("inputs","outputs"))
                modify_name2name_json_file(folder_dir,old_name,new_name)
            case 3:
                cut_front_and_back()
            case 4:
                remove_all_name_paddings()
            case 5:
                check_sequential_file_number()
            case 6:
                make_sequential_file_number()
            case 7:
                directory = choose_file_dir() 
                check_and_remove_duplicates(directory)
            case 8:
                check_duplicates()
            case 9:
                is_input_folder = input('Input Folder? (y/n/b): ').lower().strip()
                old_name = str(input("Old name:"))
                new_name = str(input("New name:"))
                
                match is_input_folder:
                    case 'y':
                        folder_dir = choose_file_dir(True)
                    case 'n':
                        folder_dir = choose_file_dir(False)
                    case 'b':
                        folder_dir = [choose_file_dir(True)] 
                        folder_dir.append(folder_dir[0].replace("inputs","outputs"))
                
                print(folder_dir)
                for folder in folder_dir:
                    replace_in_all_files(folder,
                                     old_name,
                                     new_name)
            case _:
                print("Error pls")
                import sys
                sys.exit(0)
        input("Input Anything: ")
        os.system('cls')