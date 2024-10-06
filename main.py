import os, json
from utility import (
	load_json,
	modify_json_file,
	submit_to_GPT,
	split_paragraph,
)
from openai import OpenAI
from bs4 import BeautifulSoup
rootDir = os.path.expanduser("~/cli-tool/")
OpenAI_key = load_json( os.path.join(rootDir, "APIKEY.json"))["OpenAI"]


def process_story():

	def return_story_name(mode):
		print("Choose the story name using the number")
		storylist_file = open(f"{rootDir}\\{'ch' if mode == 'translate' else 'en'}_storylist.txt", "r")
		storylist = storylist_file.read().split("\n")

		for i, story in enumerate(storylist, 1):
			print(f"{i}: {story}")
		return storylist[int(input(":"))-1]

	mode = input("Choose mode (translate/refine): ").lower()
	if mode not in ['translate', 'refine']:
		raise ValueError("Invalid mode. Choose 'translate' or 'refine'.")

	STORYNAME = return_story_name(mode)
	storyfolder = sanitize_folder_name(STORYNAME)
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
	useGPT = input("Use GPT? (y/n): ").lower() == 'y'

	if useGPT:
		client = OpenAI(api_key=api_data['openAI'])
		translation_model = "gpt-4-turbo"
		grammar_model = "gpt-4o"
	else:
		client = anthropic.Anthropic(api_key=api_data['Anthropic'])
		translation_model = grammar_model = "claude-3-5-sonnet-20240620"

	next_chapter_to_process = load_json(os.path.join(rootDir, "next-translation.json"))[STORYNAME]
	input_folder = os.path.join(rootDir, "input", "chinese" if mode == 'translate' else "english", storyfolder)
	output_folder = os.path.join(rootDir, "output-text", "chinese" if mode == 'translate' else "english", storyfolder)

	if not os.path.isdir(output_folder):
		os.makedirs(output_folder)

	try:
		for _ in range(chapters):
			print(f"Processing chapter: {next_chapter_to_process}")
			
			current_chapter_str = str(next_chapter_to_process)
			potential_names = [f"{current_chapter_str.zfill(i)}.txt" for i in range(6)]

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
				translation_message = f"""
### Mission
You are a highly skilled translator with expertise in Chinese. 
You are to accurately translate from Chinese to English following the context given. 
The USER will give you a text input and the name list. 

### Context
The context is of: {context}

### Instructions
- Only output the edited and translated version
- Preserve all dialogues.
- Minimal edits to the story.
"""
				grammar_message = """
Correct any English grammar and sentence structure error. 

### Rules
Only output the corrected version. No other comments needed
Do not edit the names, locations or key details of the story. 
Do not summarise the story.
""".strip()

			else:  # refine mode
				grammar_message = """
Correct any English grammar and sentence structure error. Sentences should make logical sense. 
Then reformat the sentences so they are connected. Sentences may be disconnected due to newlines

### Rules
Only output the corrected version. No other comments needed
Do not edit the names, locations or key details of the story. 
Do not summarise the story.""".strip()

			final_text = None
			try:
				first_chunk, second_chunk = split_paragraph(content)

				

				if mode == 'translate':
					first_chunk = f"""
### Common Names (not limited to this list)
{names}

### Story
{first_chunk}
""".strip()


					second_chunk = f"""
### Common Names (not limited to this list)
{names}

### Story
{second_chunk}
""".strip()


					temp = submit_to_AI(client, useGPT, translation_model, translation_message, first_chunk, "Translating")
					final_text = submit_to_AI(client, useGPT, grammar_model, grammar_message, temp, "Improving Grammar")
					final_text += "\n\n"
					temp = submit_to_AI(client, useGPT, translation_model, translation_message, second_chunk, "Translating")
					final_text += submit_to_AI(client, useGPT, grammar_model, grammar_message, temp, "Improving Grammar")
				else:
					final_text = submit_to_AI(client, useGPT, grammar_model, grammar_message, first_chunk, "Improving Grammar")
					final_text += "\n\n"
					final_text += submit_to_AI(client, useGPT, grammar_model, grammar_message, second_chunk, "Improving Grammar")

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
		modify_json_file(os.path.join(rootDir, "next-translation.json"), updated_json)

