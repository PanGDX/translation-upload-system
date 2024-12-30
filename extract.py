"""
Status: To be tested

Modification needed: replacing for English names
"""

import os
import re
import traceback
from langdetect import detect
import argostranslate.package
import argostranslate.translate
from utility import submit_to_GPT, load_json, get_openai_client, get_translator_using_deepl
from openai import OpenAI
import string

def translate_text(string: str) -> str:
    
    deepl_translator = get_translator_using_deepl()
    result = deepl_translator.translate_text(
        string,
        target_lang = "EN-US",
        model_type = "prefer_quality_optimized"
    )

    assert isinstance(string, str)
    from_code, to_code = "zh", "en"

    # Ensure argostranslate Chinese->English package is installed
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        (pkg for pkg in available_packages if pkg.from_code == from_code and pkg.to_code == to_code), 
        None
    )
    if package_to_install:
        argostranslate.package.install_from_path(package_to_install.download())

    return   {
        "Argos":argostranslate.translate.translate(string, from_code, to_code),
        "DeepL":result.text
    }




def extract_chinese(text: str) -> list[str]:
    assert isinstance(text, str)
    pattern = r'[\u4e00-\u9fff]+'
    return re.findall(pattern, text)


def extract_english(text: str) -> list[str]:
    assert isinstance(text, str)
    pattern = r'[A-Za-z]+'
    return re.findall(pattern, text)


def segment_list(items: list[str], segment_size: int) -> list[str]:
    # Groups a list into segments separated by new lines
    segments = []
    buffer = []
    for item in items:
        buffer.append(item)
        if len(buffer) >= segment_size:
            segments.append("\n".join(buffer))
            buffer = []
    if buffer:
        segments.append("\n".join(buffer))
    return segments


def bulk_translate_names(name_list: list[str], client: OpenAI, translation_prompt: str) -> list[str]:
    # Translate large sets of names in bulk using GPT
    segments = segment_list(name_list, 20)
    translated = []
    for seg in segments:
        try:
            translated_batch = submit_to_GPT(
                client=client,
                system_message=translation_prompt,
                user_message=seg,
                log="Translating..."
            ).split("\n")
            translated.extend(translated_batch)
        except:
            print(traceback.format_exc())
    return list(set(translated))


def reduce_names(name_list: list[str], client: OpenAI, reduction_prompt: str) -> list[str]:
    # Reduce the translated name list
    segments = segment_list(name_list, 50)
    reduced = []
    for seg in segments:
        try:
            reduced_batch = submit_to_GPT(
                client=client,
                system_message=reduction_prompt,
                user_message=seg,
                log="Reducing..."
            ).split("\n")
            reduced.extend(reduced_batch)
        except:
            print(traceback.format_exc())
    return reduced

def compare_cleaned_strings(s1: str, s2: str) -> bool:
    # Define characters to strip from both ends
    chars_to_strip = string.whitespace + string.punctuation
    
    # Strip unwanted characters from start and end of both strings
    cleaned_s1 = s1.strip(chars_to_strip)
    cleaned_s2 = s2.strip(chars_to_strip)
    
    # Compare the cleaned strings for equality
    return cleaned_s1 == cleaned_s2

def prompt_for_replacements(name_map: dict[str, str]) -> list[list[str]]:
    # Prompt user to confirm or provide final English replacements
    replace_name_list = []
    counter = 1
    print(len(name_map))
    for original_name, suggested_gpt_name in name_map.items():
        # Attempt Argos translation as a secondary suggestion
        deepl_name = ""
        argos_name = ""
        try:
            name_dict = translate_text(original_name)
            deepl_name = name_dict["DeepL"]
            argos_name = name_dict["Argos"]
        except Exception as e:
            print(e)
        

            
        prompt_text = f"""
==============================================
{counter}.
Replace '{original_name}' with? (empty = no replace)
Suggestions:
ChatGPT Direct Translate: {suggested_gpt_name}
DeepL Translate: {deepl_name if deepl_name else "No translation available"}
Argos Translate: {argos_name if argos_name else "No translation available"}
==============================================
:
"""
        print(prompt_text.strip())
        if compare_cleaned_strings(deepl_name, suggested_gpt_name) or compare_cleaned_strings(argos_name, suggested_gpt_name):
            replace_name_list.append([original_name, suggested_gpt_name])
        else:
            english_name = input()
            if english_name:
                replace_name_list.append([original_name, english_name])
            counter += 1
    return replace_name_list


def prompt_for_replacements_no_translation(name_list: list[str]) -> list[list[str]]:
    # If text is already English, no translation needed
    replace_name_list = []
    print(len(name_list))
    for i, name in enumerate(name_list, 1):
        prompt_text = f"""
==============================================
{i}.
Replace '{name}' with? (empty = no replace)
==============================================
:
"""
        english_name = input(prompt_text.strip())
        if english_name:
            replace_name_list.append([name, english_name])
    return replace_name_list


def apply_replacements(directory: str, replacements: list[list[str]]):
    # Apply name replacements to all files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if not os.path.isfile(file_path):
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            for old, new in replacements:
                content = content.replace(old, new)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except:
            print(traceback.format_exc())


def get_prompts():
    json_file_loc = os.path.join(os.getcwd(), 'json', 'prompts.json')
    content = load_json(json_file_loc)
    return content["translation-extract"], content["reduction-extract"], content["extraction-extract"]


def extract_and_replace_names(translation_prompt, reduction_prompt, extraction_prompt):
    client = get_openai_client()
    input_folder = os.path.join(os.getcwd(), "inputs")
    if not os.path.exists(input_folder):
        print("Input folder does not exist.")
        return

    # User selects story folder
    stories = os.listdir(input_folder)
    for i, story in enumerate(stories, 1):
        print(f"{i}: {story}")
    while True:
        try:
            folder_choice_index = int(input(":")) - 1
            if 0 <= folder_choice_index < len(stories):
                chosen_folder = stories[folder_choice_index]
                break
            else:
                print("Invalid choice.")
        except:
            print("Please enter a valid integer.")

    full_folder_dir = os.path.join(input_folder, chosen_folder)
    print("Selected:", chosen_folder)

    # Chapter selection
    while True:
        try:
            from_chapter = int(input("From Chapter: "))
            to_chapter = int(input("To Chapter: "))
            if from_chapter <= to_chapter:
                break
            else:
                print("From Chapter cannot be greater than To Chapter.")
        except:
            print("Invalid input.")

    # Detect language from the first chapter
    first_chapter_path = os.path.join(full_folder_dir, f'{from_chapter}.txt')
    with open(first_chapter_path, 'r', encoding='utf-8') as f:
        first_content = f.read()
    language_detected = detect(first_content)
    print(f"Language detected: {language_detected}")
    if 'zh' not in language_detected:
        raise ValueError('Has to be Chinese. No longer extracting for English either.')
    

    # Extract names from selected chapters
    final_name_list = []
    for chapter in range(from_chapter, to_chapter + 1):
        chapter_file = os.path.join(full_folder_dir, f"{chapter}.txt")
        if not os.path.isfile(chapter_file):
            print(f"Chapter file not found for chapter {chapter}. Skipping.")
            continue

        try:
            with open(chapter_file, "r", encoding="utf-8") as f:
                content = f.read().replace("\n\n", "\n")

            extracted_names = submit_to_GPT(
                client=client,
                system_message=extraction_prompt,
                user_message=content,
                log="Extracting..."
            ).split("\n")

            if language_detected == 'en':
                for line in extracted_names:
                    final_name_list.extend([nm for nm in extract_english(line) if len(nm) >= 3])
            else:
                # Assume Chinese
                for line in extracted_names:
                    final_name_list.extend([nm for nm in extract_chinese(line) if len(nm) >= 2])

        except:
            print(traceback.format_exc())
            print(f"An error occurred while processing chapter {chapter}.")

    final_name_list = sorted(list(set(final_name_list)), key=len)
    if not final_name_list:
        print("No names extracted.")
        return

    context = input("Context:")

    try:
        translation_prompt = translation_prompt.format(context=context)
        reduction_prompt = reduction_prompt.format(context=context)
    except KeyError as e:
        print(f"Error in formatting prompts: {e}")
        return

    # If Chinese text, translate and reduce
    if 'zh' in language_detected:
        translated = bulk_translate_names(final_name_list, client, translation_prompt)
        reduced = reduce_names(translated, client, reduction_prompt)

        # Create a dictionary {original_name: gpt_suggested_name}
        gpt_translated_dict = {}
        for line in reduced:
            # Lines should be of format: original - translated
            if "-" in line:
                key, val = line.split("-", 1)
                gpt_translated_dict[key.strip()] = val.strip()

        # Prompt user for final replacements
        replacements = prompt_for_replacements(gpt_translated_dict)
        apply_replacements(full_folder_dir, replacements)
    else:
        # If English text, just prompt replacements
        replacements = prompt_for_replacements_no_translation(final_name_list)
        apply_replacements(full_folder_dir, replacements)


if __name__ == '__main__':
    # Load prompts
    translation_prompt, reduction_prompt, extraction_prompt = get_prompts()
    extract_and_replace_names(
        translation_prompt=translation_prompt,
        reduction_prompt=reduction_prompt,
        extraction_prompt=extraction_prompt
    )
