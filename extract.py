import os, re
import argostranslate.package
import argostranslate.translate
from openai import OpenAI
from utility import submit_to_GPT,load_json
rootDir = os.path.expanduser("~/cli-tool/")
OpenAI_key = load_json( os.path.join(rootDir, "APIKEY.json"))["OpenAI"]
client = OpenAI(api_key= OpenAI_key)
model = "gpt-4o"
# C:\Users\User\cli-tool

translation_prompt = """
# Mission
Translate names from Chinese to English in the context of {context}. Inaccuracies are acceptable.

# Output Format
Only output the following, line by line.
(Chinese name) - (Translated English name)
No additional comments needed."""

reduction_prompt = """
# Mission
Take the names and eliminate ones that do not seem relevant to the context of {context}.
The condition for relevancy are: names of characters and names of organisations.

# Output Format
Only output the following, line by line.
(Chinese name) - (Translated English name)
No additional comments needed."""

extraction_prompt = """
# Mission
Extract all names of organisations and characters from the text and list them.

# Expected Input
A text containing a story.

# Expected Output
Only output the names, separated by a newline.""".strip()


def translate_text(string):
    from_code, to_code = "zh", "en"
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        (pkg for pkg in available_packages if pkg.from_code == from_code and pkg.to_code == to_code), None
    )
    if package_to_install:
        argostranslate.package.install_from_path(package_to_install.download())
        return argostranslate.translate.translate(string, from_code, to_code)
    return string

def extract_chinese(text):
    pattern = r'[\u4e00-\u9fff]+'
    return re.findall(pattern, text)

def sorting(lst):
    return sorted(lst, key=len)


def return_segmented_namelist(namelist:list, numberOfNames:int = 20):
    """
    @param: namelist a list of strings (names)
    @param: numberOfNames the number of names in one 'long name string'
    @return: a list of long strings of names separated by \n

    This is so that the model bulk translates instead of translating one by one. 
    """
    
    long_string_list = []
    sub_namelist = ""
    for name in namelist:
        if len(sub_namelist.split("\n")) > numberOfNames:
            long_string_list.append(sub_namelist)
            sub_namelist = ""
        sub_namelist += f"{name}\n"
    long_string_list.append(sub_namelist)
    return long_string_list




"""
Replace Chinese names with English names to maintain name coherence
"""

input_folder = os.path.join(rootDir, "inputs")    
assert(os.path.exists(input_folder))


print("Choose the folder using the number")
list_of_folders = os.listdir(input_folder)

for i, story in enumerate(list_of_folders, 1):
    print(f"{i}: {story}")
folder_choice = list_of_folders[int(input(":"))-1]

print("Selected:", folder_choice)
full_folder_dir = os.path.join(rootDir, "inputs", folder_choice)

from_chapter = int(input("From Chapter: "))
to_chapter = int(input("To Chapter: "))
finalNameList = []



try:	
    for chapter in range(from_chapter, to_chapter + 1):
        current_chapter_string = str(chapter)

        potential_names = [f"{current_chapter_string.zfill(i)}.txt" for i in range(0, 6)]
        chapter_file_dir = None
        for file_name in potential_names:
            file_path = os.path.join(full_folder_dir, file_name)
            if os.path.isfile(file_path):
                chapter_file_dir = file_path
                break
        assert(os.path.exists(chapter_file_dir))
        
        with open(chapter_file_dir, "r", encoding="utf-8") as content_file:
            content = content_file.read()
            content = content.replace("\n\n", "\n")
            content = content.replace("\n\n", "\n")

        namelist = submit_to_GPT(
            client,
            model,
            extraction_prompt,
            content,
            "Extracting..."
        ).split("\n")

        for line in namelist:
            chinese_extracted = extract_chinese(line)
            finalNameList.extend([name for name in chinese_extracted if len(name) >= 2])

except Exception as e:
    print("Error!")
    print(e)
finally:
    finalNameList = sorting(list(set(finalNameList)))

    print("Completed list processing. Eliminating unnecessary names. Please wait")
    
    context = str(input("Context:"))


    translation_prompt = translation_prompt.format(context = context)
    reduction_prompt = reduction_prompt.format(context = context)
    segmented_namelist = return_segmented_namelist(namelist, 20)
    
    translated_names = []

    for sub_namelist in segmented_namelist:
        names_translated_list = submit_to_GPT(
				client,
				model,
				translation_prompt,
				sub_namelist,
				"Translating..."
			).split("\n")
        
        
        translated_names.append(names_translated_list)

    translated_names = (list(set(translated_names)))
    segmented_translated_namelist = return_segmented_namelist(namelist, 50)
    
    final_namelist = []
    for segmented_translated_names in segmented_translated_namelist:
        reduced_translated_list = submit_to_GPT(
                    client,
                    model,
                    reduction_prompt,
                    segmented_translated_names,
                    "Reducing..."
                ).split("\n")
        final_namelist.append(reduced_translated_list)


    gpt_translated_dict = {line.split("-")[0].strip(): line.split("-")[1].strip() for line in final_namelist if line}
    
    argos_translated = {name: translate_text(name) for name in gpt_translated_dict}

    print(f"Be prepared for: {len(argos_translated)} names (BRUH)")


    replace_name_list = []
    try:
        for counter, name in enumerate(argos_translated, 1):
            gpt_name = gpt_translated_dict.get(name, "GPT Translation encountered an error/missing this name")
            english_name = input(f"""
==============================================
{counter}. 
Replace {name} with? (empty = no replace)
Suggestions:
ChatGPT Direct Translate: {gpt_name}
Translate directly: {argos_translated[name]}
==============================================
            """.strip())
            if english_name:
                replace_name_list.append([name, english_name])
                
    except Exception as e:
        print(e)
    finally:
        for [name, english_name] in replace_name_list:
            for file in os.listdir(full_folder_dir):
                with open(os.path.join(full_folder_dir, file), encoding="utf-8", mode = "r") as replace_file:
                    content = replace_file.read()
                with open(os.path.join(full_folder_dir, file), encoding="utf-8", mode = "w") as replace_file:
                    replace_file.write(content.replace(name, english_name))
                    