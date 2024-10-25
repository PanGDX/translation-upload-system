import os
import json
from utility import (
    load_json,
    submit_to_GPT,
    split_paragraph,
    get_openai_client,
    clean_filename
)
from openai import OpenAI
from bs4 import BeautifulSoup

# massive modifications needed

def return_story_name(mode):
    print("Choose the story name using the number")
    storylist_file = open(
        f"{os.getcwd()}\\{'ch' if mode == 'translate' else 'en'}_storylist.txt", "r")
    storylist = storylist_file.read().split("\n")

    for i, story in enumerate(storylist, 1):
        print(f"{i}: {story}")
    return storylist[int(input(":"))-1]

def process_story():
    client = get_openai_client()
    
    mode = input("Choose mode (translate/refine): ").lower()
    if mode not in ['translate', 'refine']:
        raise ValueError("Invalid mode. Choose 'translate' or 'refine'.")

    STORYNAME = return_story_name(mode)
    storyfolder = clean_filename(STORYNAME)
    print("In Folder: " + storyfolder)

    if mode == 'translate':
        context = input("Context of the story: ")
        names = ""
        while True:
            name_temp = input("Key Names? (empty = break): ")
            if not name_temp:
                break
            names += (name_temp + "\n")

    chapters = int(input("How many chapters to process: "))


    translation_model = grammar_model = "gpt-4o"

    next_chapter_to_process = load_json(os.path.join(
        os.getcwd(), "next-translation.json"))[STORYNAME]
    input_folder = os.path.join(
        os.getcwd(), "input", "chinese" if mode == 'translate' else "english", storyfolder)
    output_folder = os.path.join(
        os.getcwd(), "output-text", "chinese" if mode == 'translate' else "english", storyfolder)

    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    try:
        for _ in range(chapters):
            print(f"Processing chapter: {next_chapter_to_process}")

            current_chapter_str = str(next_chapter_to_process)
            potential_names = [
                f"{current_chapter_str.zfill(i)}.txt" for i in range(6)]

            chapter_file_dir = None
            for file_name in potential_names:
                file_path = os.path.join(input_folder, file_name)
                if os.path.isfile(file_path):
                    chapter_file_dir = file_path
                    break

            outputchapter = sorted(
                os.listdir(output_folder),
                key=lambda name: int(name.split('.')[0])
            )[-1]
            outputchapter = f"{int(outputchapter.split('.')[0]) + 1}.txt"

            print(chapter_file_dir)
            if chapter_file_dir is None:
                raise FileNotFoundError("Chapter file not found")

            with open(chapter_file_dir, "r", encoding="utf-8") as content_file:
                content = content_file.read().replace("\n\n", "\n")

            if mode == 'translate':
                translation_message = f""""""
                grammar_message = """""".strip()

            else:  # refine mode
                grammar_message = """""".strip()

            final_text = None
            try:
                first_chunk, second_chunk = split_paragraph(content)

                if mode == 'translate':
                    first_chunk = f"""""".strip()

                    second_chunk = f"""""".strip()

                    temp = submit_to_GPT(
                        client, translation_model, translation_message, first_chunk, "Translating")
                    final_text = submit_to_GPT(
                        client, grammar_model, grammar_message, temp, "Improving Grammar")
                    final_text += "\n\n"
                    temp = submit_to_GPT(
                        client, translation_model, translation_message, second_chunk, "Translating")
                    final_text += submit_to_GPT(client, grammar_model,
                                               grammar_message, temp, "Improving Grammar")
                else:
                    final_text = submit_to_GPT(
                        client, grammar_model, grammar_message, first_chunk, "Improving Grammar")
                    final_text += "\n\n"
                    final_text += submit_to_GPT(client, grammar_model,
                                               grammar_message, second_chunk, "Improving Grammar")

            except Exception as e:
                print("ERROR OCCURRED\n", e)

            if final_text is not None:
                with open(os.path.join(output_folder, outputchapter), "w", encoding="utf-8") as append_to_file:
                    append_to_file.write(str(final_text))
                next_chapter_to_process += 1
            else:
                raise Exception("Error in processing!!!!")
    except Exception as e:
        print(e)
    finally:
        updated_json = {STORYNAME: next_chapter_to_process}
        modify_json_file(os.path.join(
            os.getcwd(), "next-translation.json"), updated_json)
