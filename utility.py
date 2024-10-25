import os
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from openai import OpenAI


def load_json(file_path):
    if file_path and not file_path.endswith(".json"):
        file_path += ".json"

    assert ('.json' in file_path)

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    else:
        raise FileNotFoundError


def split_paragraph(text):
	midpoint = len(text) // 2
	closest_newline = text.find('\n', midpoint)

	if closest_newline == -1:
		# If no newline character is found, search backwards from the midpoint.
		closest_newline = text.rfind('\n', 0, midpoint)
		if closest_newline == -1:
			# If still no newline character, split at the midpoint.
			closest_newline = midpoint

	part1 = text[:closest_newline].strip()
	part2 = text[closest_newline:].strip()

	return part1, part2


# make into two functions: modify json file for name2name and data.json

def modify_name2name_json_file(full_story_name, old_name, new_name):
    """
    Add a new name to do replace old_name with.


    name2name.json has the format:
    {"story name":{
            "oldname" : ["new1", "new2"]
        }
    }
    """
    file_path = os.path.join(rootdir, "json", "name2name.json")
    with open(file_path, 'r') as file:
        data = json.load(file)

   assert(data[full_story_name])

def modify_data_json_file(new_data_json:dict, isReplacing:bool  = True):
    """
    Add data_json into existing json file content and saves it. 
    If the element already exists, the new data will replace the old one by default
    Set isReplacing = false to not replace existing content.
    
    new_data_json has to be in the format:
    {"full story name" : {some data}}
    """
    file_path = os.path.join(rootdir, "json", "data.json") 
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    assert( (story in data) for story in list(new_data_json.keys()) )

    with open(file_path, 'w') as file:
        json.dump(merged_data, file, indent=4)


def submit_to_GPT(client, model:str, system_message, user_message, log:str = ""):
    completion = client.chat.completions.create(
        model=model,
        max_tokens = 4095,
        messages=[{"role": "system", "content": system_message}, 
                    {"role": "user", "content": user_message}
                    ],
    )
    if(log!=""): print(log)

    return completion.choices[0].message.content

def append_and_clean(file_path, text):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    lines = [line for line in lines if line.strip()]
    lines.append(text + '\n')
    with open(file_path, 'w') as file:
        file.writelines(lines)

def count_words(string):
    words = string.split()
    print(len(words))

def clean_filename(filename: str) -> str:
    """
    Formats filenames and folders to fit Window's conventions
    """
    cleaned = re.sub(r'[^\w\s\-\.\_]', '', filename)
    cleaned = cleaned.strip('.')
    return cleaned



def add_story(full_story_name:str, patreon_story_name:str):
    output_folder = clean_filename(full_story_name)

    full_dir = os.path.join("inputs", output_folder)
    os.makedirs(full_dir, exist_ok = True)

    modify_json_file(
            file_path=os.path.join("data.json"),
            appendJson={
                full_story_name: {
                    "Next Translated Chapter": 1,
                    "Next Inkstone Chapter": 1,
                    "Next Patreon Chapter": 1,
                    "Patreon Category": patreon_story_name
                    }
                }
            )
    return output_folder

def setup_chrome_driver():
    chromedriver_path = "chromedriver.exe"
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=C:\\Users\\User\\AppData\\Local\\Google\\Chrome\\User Data")
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)

def get_openai_client():
    api_loc = os.path.join(os.getcwd(),'json','APIKEY.json')
    OpenAI_key = load_json(api_loc)["OpenAI"]
    client = OpenAI(api_key=OpenAI_key)