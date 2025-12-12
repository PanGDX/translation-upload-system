import os
import json
import traceback
from langdetect import detect
from old.utility import (
    load_json,
    submit_to_GPT,
    split_paragraph,
    get_openai_client,
    clean_file_name,
    get_translator_using_deepl
)

def translate_text_deepl(string: str) -> str:
    deepl_translator = get_translator_using_deepl()
    result = deepl_translator.translate_text(
        string,
        target_lang="EN-US",
        model_type="prefer_quality_optimized"
    )
    print(result)
    return result.text

def process_stories(is_using_gpt_for_translation: bool = True):
    """
    This function allows you to queue multiple stories, along with context and other parameters,
    and then processes them all at once.
    """
    client = get_openai_client()

    # Load JSON data
    story_data_json = load_json(os.path.join(os.getcwd(), 'json', 'data.json'))
    prompt_json = load_json(os.path.join(os.getcwd(), 'json', 'prompts.json'))

    # Get all story names
    storylist = list(story_data_json.keys())

    # Display available stories
    print("Available stories:")
    for i, story in enumerate(storylist, 1):
        print(f"{i}: {story}")

    # Ask how many stories to queue
    number_of_stories = int(input("\nHow many stories do you want to queue? "))

    # We'll store all the queued stories in a list of dictionaries
    queued_stories = []

    # Collect story parameters for each queued story
    for _ in range(number_of_stories):
        chosen_index = int(input("\nChoose the story index: ")) - 1
        story_name = storylist[chosen_index]

        # Prepare input folder
        input_story_folder = os.path.join(os.getcwd(), "inputs", clean_file_name(story_name))
        # Prepare output folder
        output_story_folder = os.path.join(os.getcwd(), "outputs", clean_file_name(story_name))

        if not os.path.exists(output_story_folder):
            os.mkdir(output_story_folder)
            print(f"Created output folder for: {story_name}")

        print(f"\nStory chosen: {story_name}")
        print("Input folder:", input_story_folder)

        # Number of chapters to process
        chapters_to_process = int(input("How many chapters to process: "))

        # Determine which chapter to start from
        next_input_chapter = story_data_json[story_name]["Next Translated Chapter"]

        # For language detection, grab the sample from the next chapter
        sample_file_path = os.path.join(input_story_folder, f"{next_input_chapter}.txt")
        if not os.path.exists(sample_file_path):
            raise FileNotFoundError(f"Sample file not found at {sample_file_path}")

        with open(sample_file_path, 'r', encoding='utf-8') as sample_file:
            sample_content = sample_file.read()
        lang_detected = detect(sample_content)
        print(f'Language detected for {story_name}: {lang_detected}')
        if ('zh' not in lang_detected) and ('en' != lang_detected):
            raise ValueError("Wrong Language!!!!")

        # Additional context
        context = input("Context of the story: ")

        # For Chinese stories, we also want to gather a list of key names
        names = ""
        if 'zh' in lang_detected:
            print("Enter key names (leave empty to finish):")
            while True:
                name_temp = input("> ")
                if not name_temp:
                    break
                names += (name_temp + "\n")

        # Save all the collected info in a dictionary
        queued_stories.append({
            "story_name": story_name,
            "input_folder": input_story_folder,
            "output_folder": output_story_folder,
            "next_input_chapter": next_input_chapter,
            "chapters_to_process": chapters_to_process,
            "lang_detected": lang_detected,
            "context": context,
            "names": names
        })

    # Now that all stories are queued, process them one by one
    for story_info in queued_stories:
        story_name = story_info["story_name"]
        input_story_folder = story_info["input_folder"]
        output_story_folder = story_info["output_folder"]
        next_input_chapter = story_info["next_input_chapter"]
        chapters = story_info["chapters_to_process"]
        lang_detected = story_info["lang_detected"]
        context = story_info["context"]
        names = story_info["names"]

        print(f"\n--- Processing queued story: {story_name} ---")

        # Create the translation message if language is Chinese
        if 'zh' in lang_detected:
            translation_message = prompt_json["translation-translate"]
            translation_message = translation_message.format(
                context=context,
                names=names
            )
        else:
            translation_message = None

        # Create the grammar message
        grammar_message = prompt_json["grammar-translate"]
        grammar_message = grammar_message.format(context=context)

        # Process each chapter
        try:
            for _ in range(chapters):
                print(f"\nProcessing chapter: {next_input_chapter}")

                input_chapter_file_dir = os.path.join(
                    input_story_folder, f"{next_input_chapter}.txt")
                output_chapter_file_dir = os.path.join(
                    output_story_folder, f"{next_input_chapter}.txt")

                if not os.path.exists(input_chapter_file_dir):
                    raise FileNotFoundError(f"Chapter file {input_chapter_file_dir} not found")

                with open(input_chapter_file_dir, "r", encoding="utf-8") as content_file:
                    content = content_file.read().replace("\n\n", "\n")

                final_text = None
                try:
                    first_chunk, second_chunk = split_paragraph(content)

                    # If source language is Chinese
                    if 'zh' in lang_detected:
                        # 1. Translate + grammar check first_chunk
                        if is_using_gpt_for_translation:
                            temp = submit_to_GPT(
                                client=client,
                                system_message=translation_message,
                                user_message=first_chunk,
                                log="Translating"
                            )
                        else:
                            temp = translate_text_deepl(first_chunk)
                            print("Used DeepL for chunk 1 translation")

                        final_text = submit_to_GPT(
                            client=client,
                            system_message=grammar_message,
                            user_message=temp,
                            log="Improving Grammar"
                        ) + "\n\n"

                        # 2. Translate + grammar check second_chunk
                        secondary_translation_message = (
                            translation_message + 
                            f"\n### Previous Chapter: Make sure the names are aligned\n{final_text}"
                        )

                        if is_using_gpt_for_translation:
                            temp = submit_to_GPT(
                                client=client,
                                system_message=secondary_translation_message,
                                user_message=second_chunk,
                                log="Translating"
                            )
                        else:
                            temp = translate_text_deepl(second_chunk)
                            print("Used DeepL for chunk 2 translation")

                        final_text += submit_to_GPT(
                            client=client,
                            system_message=grammar_message,
                            user_message=temp,
                            log="Improving Grammar"
                        )
                    else:
                        # If source language is English
                        final_text = submit_to_GPT(
                            client=client,
                            system_message=grammar_message,
                            user_message=first_chunk,
                            log="Improving Grammar"
                        ) + "\n\n"
                        final_text += submit_to_GPT(
                            client=client,
                            system_message=grammar_message,
                            user_message=second_chunk,
                            log="Improving Grammar"
                        )

                except Exception as e:
                    print(traceback.format_exc())
                    print("ERROR OCCURRED\n", e)

                if final_text is not None:
                    with open(output_chapter_file_dir, "w", encoding="utf-8") as outfile:
                        outfile.write(str(final_text))
                    next_input_chapter += 1
                else:
                    raise Exception("Error in processing!!!!")

        except Exception as e:
            print(traceback.format_exc())
            print(e)
        finally:
            # Update JSON with the new "Next Translated Chapter"
            story_data_json[story_name]["Next Translated Chapter"] = next_input_chapter
            json_object = json.dumps(story_data_json, indent=4)
            with open(os.path.join(os.getcwd(), 'json', 'data.json'), "w", encoding='utf-8') as outfile:
                outfile.write(json_object)

        print(f"Finished processing {story_name}")

    print("\nAll queued stories processed!")

if __name__ == '__main__':
    is_using_gpt_for_translation = str(input("Use GPT-4 for translation? (y/n): ")).lower().strip() == 'y'
    process_stories(is_using_gpt_for_translation)
