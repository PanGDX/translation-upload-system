import os
import re
import argostranslate.package
import argostranslate.translate
from utility import submit_to_GPT, load_json, get_openai_client
import traceback

def translate_text(string: str) -> str:
    """
    ### @param string: input string to be translated
    ### @return: output the translated string

    Translated the string from Chinese to English.
    Installs argotranslate Chinese package if it is not installed
    """

    assert (type(string) == str)

    from_code, to_code = "zh", "en"
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        (pkg for pkg in available_packages if pkg.from_code ==
         from_code and pkg.to_code == to_code), None
    )
    if package_to_install:
        argostranslate.package.install_from_path(package_to_install.download())
    return argostranslate.translate.translate(string, from_code, to_code)


def extract_chinese(text: str):
    """
    ### @param text: A mix of Chinese and English text in a line
    ### @output: all the Chinese text in a list
    """
    assert (type(text) == str)

    pattern = r'[\u4e00-\u9fff]+'
    return re.findall(pattern, text)


def return_segmented_name_list(name_list: list[str], number_of_names: int = 20):
    """
    ### @param name_list: a list of strings (names)
    ### @param number_of_names: the number of names in one 'long name string'
    ### @return: a list of long strings of names separated by \n

    This is so that the  bulk translates instead of translating one by one. 
    """

    for name in name_list:
        assert (type(name) == str)

    long_string_list = []
    sub_name_list = ""
    for name in name_list:
        if len(sub_name_list.split("\n")) > number_of_names:
            long_string_list.append(sub_name_list)
            sub_name_list = ""
        sub_name_list += f"{name}\n"
    long_string_list.append(sub_name_list)
    return long_string_list


def get_prompts():
    """
    ### @return: three prompts (paragraphs) - for translation, reduction and extraction respectively 
    """
    json_file_loc = os.path.join(os.getcwd(), 'json', 'prompts.json')
    content = load_json(json_file_loc)
    return content["translation-extract"], content["reduction-extract"], content["extraction-extract"]


def extract_and_replace_names(translation_prompt, reduction_prompt, extraction_prompt):
    """
    ### @param translation_prompt: prompt for translation
    ### @param reduction_prompt: prompt for removing redundant/rare names
    ### @param extraction_prompt: prompt for extracting names from the text

    Replace Chinese names with English names to maintain name coherence using GPT-4o
    """

    client = get_openai_client()
    input_folder = os.path.join(os.getcwd(), "inputs")
    if not os.path.exists(input_folder):
        print("Input folder does not exist.")
        return
    final_name_list = []

    print("Choose the folder using the number")
    list_of_folders = os.listdir(input_folder)

    for i, story in enumerate(list_of_folders, 1):
        print(f"{i}: {story}")
    while True:
        try:
            folder_choice_index = int(input(":")) - 1
            if folder_choice_index < 0 or folder_choice_index >= len(list_of_folders):
                raise IndexError("Invalid folder selection.")
            folder_choice = list_of_folders[folder_choice_index]
            break
        except ValueError:
            print("Please enter a valid integer.")
        except IndexError as ie:
            print(str(ie))
        except Exception as e:
            print(traceback.format_exc())
            print(e)
    print("Selected:", folder_choice)
    full_folder_dir = os.path.join(os.getcwd(), "inputs", folder_choice)

    while True:
        try:
            from_chapter = int(input("From Chapter: "))
            to_chapter = int(input("To Chapter: "))
            if from_chapter > to_chapter:
                print("From Chapter cannot be greater than To Chapter.")
                continue
            break
        except ValueError:
            print("Please enter valid integers for chapters.")

    for chapter in range(from_chapter, to_chapter + 1):
        chapter_file_dir = os.path.join(full_folder_dir, f"{chapter}.txt")
        if not chapter_file_dir:
            print(f"Chapter file not found for chapter {chapter}. Skipping.")
            continue  # Skip to the next chapter
        try:
            with open(chapter_file_dir, "r", encoding="utf-8") as content_file:
                content = content_file.read()
                content = content.replace("\n\n", "\n")
                content = content.replace("\n\n", "\n")

            name_list = submit_to_GPT(
                client = client,
                system_message=extraction_prompt,
                user_message=content,
                log="Extracting..."
            ).split("\n")

            for line in name_list:
                chinese_extracted = extract_chinese(line)
                final_name_list.extend(
                    [name for name in chinese_extracted if len(name) >= 2])
        except Exception as e:
            print(traceback.format_exc())
            print(f"An error occurred while processing chapter {chapter}: {e}")
            continue  # Skip to next chapter

    final_name_list = sorted(list(set(final_name_list)), key=len)

    if not final_name_list:
        print("No names were extracted from the chapters.")
        return  # Exit the function early

    print("Completed list processing. Eliminating unnecessary names. Please wait")

    context = str(input("Context:"))

    try:
        translation_prompt = translation_prompt.format(context=context)
        reduction_prompt = reduction_prompt.format(context=context)
    except KeyError as e:
        print(f"Error in formatting prompts: {e}")
        return

    segmented_name_list = return_segmented_name_list(final_name_list, 20)

    translated_names = []

    for sub_name_list in segmented_name_list:
        try:
            names_translated_list = submit_to_GPT(
                client=client,
                system_message=translation_prompt,
                user_message=sub_name_list,
                log="Translating..."
            ).split("\n")
            translated_names.extend(names_translated_list)
        except Exception as e:
            print(traceback.format_exc())
            print(f"Error during translation: {e}")
            continue  # Continue with next sub_name_list

    translated_names = list(set(translated_names))  # Remove duplicates
    segmented_translated_name_list = return_segmented_name_list(
        translated_names, 50)

    final_name_list = []
    for segmented_translated_names in segmented_translated_name_list:
        try:
            reduced_translated_list = submit_to_GPT(
                client=client,
                system_message=reduction_prompt,
                user_message=segmented_translated_names,
                log="Reducing..."
            ).split("\n")
            final_name_list.extend(reduced_translated_list)
        except Exception as e:
            print(traceback.format_exc())
            print(f"Error during reduction: {e}")
            continue  # Continue with next segmented_translated_names

    gpt_translated_dict = {}
    for line in final_name_list:
        if "-" in line:
            parts = line.split("-")
            key = parts[0].strip()
            value = "-".join(parts[1:]).strip()
            gpt_translated_dict[key] = value
        else:
            print(f"Line '{line}' does not contain '-', skipping.")

    argos_translated = {}
    for name in gpt_translated_dict:
        try:
            translation = translate_text(name)
            argos_translated[name] = translation
        except Exception as e:
            print(traceback.format_exc())
            print(f"Error translating name '{name}' using argos_translate: {e}")
            argos_translated[name] = ""

    print(f"Be prepared for: {len(argos_translated)} names")

    replace_name_list = []
    try:
        for counter, name in enumerate(argos_translated, 1):
            gpt_name = gpt_translated_dict.get(
                name, "GPT Translation missing this name")
            argos_name = argos_translated.get(name, "Argos Translation missing this name")
            prompt_text = f"""
==============================================
{counter}.
Replace '{name}' with? (empty = no replace)
Suggestions:
ChatGPT Direct Translate: {gpt_name}
Argos Translate: {argos_name}
==============================================
            """
            english_name = input(prompt_text.strip())
            if english_name:
                replace_name_list.append([name, english_name])
    except KeyboardInterrupt:
        print("\nUser interrupted the process.")
    except Exception as e:
        print(traceback.format_exc())
        print(f"An error occurred during name replacement: {e}")

    for [name, english_name] in replace_name_list:
        for file in os.listdir(full_folder_dir):
            file_path = os.path.join(full_folder_dir, file)
            if not os.path.isfile(file_path):
                continue
            try:
                with open(file_path, encoding="utf-8", mode="r") as replace_file:
                    content = replace_file.read()
                content = content.replace(name, english_name)
                with open(file_path, encoding="utf-8", mode="w") as replace_file:
                    replace_file.write(content)
            except Exception as e:
                print(traceback.format_exc())
                print(f"Error replacing names in file '{file}': {e}")
                continue  # Continue with next file


if __name__ == '__main__':
    print("Extract + Replace Names")
    translation_prompt, reduction_prompt, extraction_prompt = get_prompts()
    extract_and_replace_names(translation_prompt=translation_prompt,
        reduction_prompt=reduction_prompt,
        extraction_prompt=extraction_prompt)