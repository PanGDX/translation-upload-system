import os
import json
from utility import (
    load_json,
    submit_to_GPT,
    split_paragraph,
    get_openai_client,
    clean_file_name
)
from langdetect import detect
import traceback

# massive modifications needed

def process_story():
    client = get_openai_client()

    print("Choose the story name using the number")
    story_data_json = load_json(os.path.join(os.getcwd(), 'json', 'data.json'))
    prompt_json = load_json(os.path.join(os.getcwd(), 'json', 'prompts.json'))

    storylist = list(story_data_json.keys())

    for i, story in enumerate(storylist, 1):
        print(f"{i}: {story}")
    story_name = storylist[int(input("Choose: ")) - 1]
    input_story_folder = os.path.join(
        os.getcwd(), "inputs", clean_file_name(story_name))
    output_story_folder = os.path.join(
        os.getcwd(), "outputs", clean_file_name(story_name))

    print("In Folder: " + input_story_folder)

    sample_file = open(os.path.join(input_story_folder,
                       "1.txt"), 'r', encoding='utf-8').read()
    lang_detected = detect(sample_file)
    print(f'Language detected: {lang_detected}')
    if ('zh' not in lang_detected) and ('en' != lang_detected):
        raise ValueError("Wrong Language!!!!")
    # en, zh-cn, zh-tw

    if 'zh' in lang_detected:
        context = input("Context of the story: ")
        names = ""
        while True:
            name_temp = input("Key Names? (empty = break): ")
            if not name_temp:
                break
            names += (name_temp + "\n")

    chapters = int(input("How many chapters to process: "))

    next_input_chapter = story_data_json[story_name]["Next Translated Chapter"]
    if not os.path.isdir(output_story_folder):
        os.makedirs(output_story_folder)
        next_output_chapter = 1
    elif not os.path.exists(os.path.join(output_story_folder, '1.txt')):
        next_output_chapter = 1
    else:
        next_output_chapter = sorted(
            os.listdir(output_story_folder),
            key=lambda name: int(name.split('.')[0])
        )[-1]


    if 'zh' in lang_detected:
        translation_message = prompt_json["translation-translate"]
        translation_message = translation_message.format(
                    context=context,
                    names=names
        )
        print(translation_message)
    grammar_message = prompt_json["grammar-translate"]

    try:
        for _ in range(chapters):
            print(f"Processing chapter: {next_input_chapter}")

            input_chapter_file_dir = os.path.join(
                input_story_folder, f"{next_input_chapter}.txt")
            output_chapter_file_dir = os.path.join(
                output_story_folder, f"{next_output_chapter}.txt")

            print(input_chapter_file_dir)
            if input_chapter_file_dir is None:
                raise FileNotFoundError("Chapter file not found")

            with open(input_chapter_file_dir, "r", encoding="utf-8") as content_file:
                content = content_file.read().replace("\n\n", "\n")


            final_text = None
            try:
                first_chunk, second_chunk = split_paragraph(content)

                if 'zh' in lang_detected:
                    temp = submit_to_GPT(
                        client=client,
                        system_message=translation_message,
                        user_message=first_chunk,
                        log="Translating")
                    final_text = submit_to_GPT(
                        client=client, 
                        system_message=grammar_message, 
                        user_message=temp, 
                        log="Improving Grammar")

                    final_text += "\n\n"

                    secondary_translation_message = translation_message + f"\n### Previous Chapter: Make sure the names are aligned\n{final_text}"
                    temp = submit_to_GPT(
                        client=client, 
                        system_message=secondary_translation_message, 
                        user_message=second_chunk, 
                        log="Translating")
                    final_text += submit_to_GPT(
                        client=client, 
                        system_message=grammar_message, 
                        user_message=temp, 
                        log="Improving Grammar")
                else:
                    final_text = submit_to_GPT(
                        client=client, 
                        system_message=grammar_message, 
                        user_message=first_chunk, 
                        log="Improving Grammar")
                    final_text += "\n\n"
                    final_text += submit_to_GPT(
                        client=client, 
                        system_message=grammar_message, 
                        user_message=second_chunk, 
                        log="Improving Grammar")

            except Exception as e:
                print(traceback.format_exc())
                print("ERROR OCCURRED\n", e)

            if final_text is not None:
                with open(output_chapter_file_dir, "w", encoding="utf-8") as outfile:
                    outfile.write(str(final_text))
                next_input_chapter += 1
                next_output_chapter += 1
            else:
                raise Exception("Error in processing!!!!")
    except Exception as e:
        print(traceback.format_exc())
        print(e)
    finally:
        story_data_json[story_name]["Next Translated Chapter"] = next_input_chapter
        json_object = json.dumps(story_data_json, indent=4)

        with open(os.path.join(os.getcwd(), 'json', 'data.json'), "w", encoding='utf-8') as outfile:
            outfile.write(json_object)


if __name__ == '__main__':
    process_story()
