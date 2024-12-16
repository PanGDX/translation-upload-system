import os
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager



# Functions that concern the management and updating of files and folders and their contents

def load_json(file_path: str) -> dict:
    """
    ### @param file_path: a string that is the absolute file path
    ### @return: a dictionary (json file content)

    If the file does not exist, the function raises a FileNotFoundError
    """
    if file_path and not file_path.endswith(".json"):
        file_path += ".json"

    assert ('.json' in file_path)

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    else:
        raise FileNotFoundError


def split_paragraph(text: str) -> tuple[str, str]:
    """
    ### @param text: a paragraph
    ### @return: returns the paragraph divided into two portions of close-to-equal size
    """
    midpoint = len(text) // 2
    closest_newline = text.find('\n', midpoint)

    if closest_newline == -1:
        closest_newline = text.rfind('\n', 0, midpoint)
        if closest_newline == -1:
            closest_newline = midpoint

    part1 = text[:closest_newline].strip()
    part2 = text[closest_newline:].strip()

    return part1, part2


def modify_name2name_json_file(full_story_name: str, old_name: str, new_name: str):
    """
    ### @param full_story_name
    ### @param old_name: old name to be replaced
    ### @param new_name: new name to use to replace
    Add a new name to do replace old_name with.


    name2name.json has the format:
    {
        "story name":
            {
                "new_name" : ["old1", "old2"]
            }
    }
    """
    file_path = os.path.join(os.getcwd(), "json", "name2name.json")
    with open(file_path, 'r') as file:
        data = json.load(file)

    if full_story_name not in data:
        data[full_story_name] = {}

    if (new_name not in data[full_story_name]):
        data[full_story_name][new_name] = []

    assert (type(data[full_story_name][new_name]) == list)
    data[full_story_name][new_name].append(old_name)

    json_object = json.dumps(data, indent=4)
    name2name_dir = os.path.join(os.getcwd(), 'json', 'name2name.json')
    with open(name2name_dir, "w") as outfile:
        outfile.write(json_object)


def modify_data_json_file(
        full_story_name: str,
        patreon_category: str,
        next_translated: int = 1,
        next_inkstone: int = 1,
        next_patreon: int = 1):
    """
    ### @param full_story_name
    ### @param patreon_category: the name of the story on Patreon's dropdown bar
    ### @param next_translated: next chapter to be translated. Default is 1
    ### @param next_inkstone: next chapter to be uploaded on inkstone. Default is 1
    ### @param next_patreon: next chapter to be uploaded on patreon. Default is 1

    WILL replace the existing information. If the data does not exist, it will create it.


    data.json is in the format:
    {
        "story 1":{
            "Next Translated Chapter": next_translated,
            "Next Inkstone Chapter": next_inkstone,
            "Next Patreon Chapter": next_patreon,
            "Patreon Category": patreon_category
        },
        "story 2": {
            ...
        }
    }
    """
    file_path = os.path.join(os.getcwd(), "json", "data.json")
    with open(file_path, 'r') as file:
        data = json.load(file)

    if full_story_name not in data:
        data[full_story_name] = {}

    """
        patreon_category: str,
        next_translated: int = 1,
        next_inkstone: int = 1,
        next_patreon: int = 1,
    """

    data[full_story_name]["Patreon Category"] = patreon_category
    data[full_story_name]["Next Inkstone Chapter"] = next_inkstone
    data[full_story_name]["Next Translated Chapter"] = next_translated
    data[full_story_name]["Next Patreon Chapter"] = next_patreon

    json_object = json.dumps(data, indent=4)
    name2name_dir = os.path.join(os.getcwd(), 'json', 'data.json')
    with open(name2name_dir, "w") as outfile:
        outfile.write(json_object)



def clean_file_name(file_name: str) -> str:
    """
    ### @param file_name: the file_name or folder name to be cleaned up

    Formats file_names and folders to fit Window's conventions
    """
    cleaned = re.sub(r'[^\w\s\-\.\_]', '', file_name)
    cleaned = cleaned.strip('.')
    return cleaned


def add_story(full_story_name: str, patreon_story_name: str) -> str:
    """
    ### @param full_story_name: the full story name
    ### @param patreon_story_name: the patreon category name
    ### @return: the output folder's name that has been formatted

    WILL replace patreon_story_name if the category already exists.
    """

    output_folder = clean_file_name(full_story_name)

    full_dir = os.path.join("inputs", output_folder)
    os.makedirs(full_dir, exist_ok=True)

    modify_data_json_file(
        full_story_name=full_story_name,
        patreon_category=patreon_story_name,
    )
    return output_folder




# Functiosn that concern drivers and interactions with GPT 

def setup_chrome_driver(is_headless = False) -> webdriver.Chrome:
    print("Make sure to close existing Chrome or else an error may occur")
    time.sleep(2)


    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument(
        "user-data-dir=C:\\Users\\User\\AppData\\Local\\Google\\Chrome\\User Data"
    )

    # Remove or adjust unsupported flags
    # If you need headless mode, try the older headless flag:
    if is_headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # This argument can help address deprecated fallback issues if needed
    chrome_options.add_argument("--enable-unsafe-swiftshader")


    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)
    return driver


def get_openai_client() -> OpenAI:
    api_loc = os.path.join(os.getcwd(), 'json', 'APIKEY.json')
    OpenAI_key = load_json(api_loc)["OpenAI"]
    client = OpenAI(api_key=OpenAI_key)
    return client



def submit_to_GPT(client: OpenAI, system_message: str, user_message: str, model: str = "gpt-4o", log: str = "") -> str:
    """
    ### @param client: OpenAI client
    ### @param system_message: the system prompt
    ### @param user_message: the user prompt
    ### @param model: the model to be used, default: gpt-4o
    ### @param log: a string printed when the function is ran
    """
    completion = client.chat.completions.create(
        model=model,
        max_tokens=4095,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
    )
    if (log != ""):
        print(log)

    return completion.choices[0].message.content