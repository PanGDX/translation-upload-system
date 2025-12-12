import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.service import Service
from old.utility import setup_chrome_driver, clean_file_name, load_json

# Set up logging so that all Selenium logs go to a file instead of the terminal
logging.basicConfig(
    filename="selenium_driver.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


def save_json(path: str, data):
    """
    Stub function: saves data to JSON file
    """
    import json
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)





def upload_to_patreon(category: str, chapter_title: str, content: str, driver: webdriver.Chrome):
    """
    Upload a chapter to Patreon.
    """

    try:
        button_xpath = "//button[contains(., 'Create')]"
        button_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, button_xpath))
        )
        button_element.click()

        print("Inserting title")
        title_input_xpath = "//textarea[@aria-label='Title']"
        title_input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, title_input_xpath))
        )
        title_input_element.send_keys(chapter_title)


        print("Inserting Body")
        body_input_xpath = "//div[@contenteditable='true' and @class='ProseMirror remirror-editor']"
        body_input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, body_input_xpath))
        )
        body_input_element.send_keys(content)


        print("Choosing category")
        category_access_xpath = "//button[@id='collections-list-dropdown']"
        category_access_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, category_access_xpath))
        )
        category_access_element.click()

        category_access_xpath = f'//li[contains(., "{category}")]'
        category_access_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, category_access_xpath))
        )
        category_access_element.click()

        next_button_xpath = "//button[contains(., 'Next') and @type='button']"
        next_button_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, next_button_xpath))
        )
        next_button_element.click()

        publish_button_xpath = "//button[contains(., 'Publish') and @type='button']"
        publish_button_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, publish_button_xpath))
        )
        publish_button_element.click()
 
        share_button_xpath = "//button[@aria-label='Close the share dialog']"
        share_button_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, share_button_xpath))
        )
        share_button_element.click()

        time.sleep(2)

    except Exception as e:
        print(f"[Patreon Upload Error] {e}")
        # Keep the driver open so that errors can be observed
        # No driver.quit() here.


def upload_to_inkstone(story: str, chapter_title: str, content: str, driver: webdriver.Chrome, in_create_page: bool = False):
    """
    Upload a chapter to Inkstone.
    """

    try:
        if not in_create_page:
            story_div_xpath = f'//tr[contains(., "{story}")]'
            story_div_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, story_div_xpath))
            )

            explore_button_xpath = ".//button[@data-report-uiname='explore']"
            explore_button = story_div_element.find_element(By.XPATH, explore_button_xpath)
            explore_button.click()

        create_button_xpath = "//button[contains(., 'CREATE CHAPTER')]"
        create_button_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, create_button_xpath))
        )
        create_button_element.click()

        time.sleep(2)


        div_xpath = "//div[contains(@class, 'tox-edit-area')]//iframe"
        iframe_element = driver.find_element(By.XPATH, div_xpath)
        driver.switch_to.frame(iframe_element)

        body_input_xpath = "//body[@id='tinymce' and @contenteditable='true']"
        body_input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, body_input_xpath))
        )
        body_input_element.send_keys(content)

        driver.switch_to.default_content()

        title_input_xpath = "//input[@type='text' and @placeholder='Title Here']"
        title_input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, title_input_xpath))
        )
        title_input_element.send_keys(chapter_title)

        publish_button_xpath = "//button[span[contains(., 'Publish')]]"
        publish_button_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, publish_button_xpath))
        )
        publish_button_element.click()

        confirm_button_xpath = "//button[contains(., 'confirm')]"
        confirm_button_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, confirm_button_xpath))
        )
        confirm_button_element.click()

        time.sleep(5)

    except Exception as e:
        print(f"[Inkstone Upload Error] {e}")
        # Keep the driver open so that errors can be observed
        # No driver.quit() here.


def double_upload(chapters: int, full_story_name: str, comments: str = "", platform: str = "both"):
    """
    @param chapters: number of chapters to upload
    @param full_story_name: the story name
    @param platform: 'patreon', 'inkstone', or 'both'
    """

    # Start driver

    data_json = load_json(os.path.join(os.getcwd(), 'json', 'data.json'))
    if full_story_name not in data_json:
        print(f"No data for story: {full_story_name}")
        return

    data = data_json[full_story_name]
    story_name_dir = clean_file_name(full_story_name)
    patreon_category = data["Patreon Category"]
    current_inkstone_chapter = data["Next Inkstone Chapter"]
    current_patreon_chapter = data["Next Patreon Chapter"]

    # If uploading to Inkstone, ask for optional comments


    driver = setup_chrome_driver()
    # Upload to Inkstone if requested
    if platform in ["both", "inkstone"]:
        driver.get("https://inkstone.webnovel.com/novels/list?story=1")
        time.sleep(10)
        in_create_page = False
        for _ in range(chapters):
            file_path = os.path.join(
                os.getcwd(), "outputs", story_name_dir, f"{current_inkstone_chapter}.txt"
            )
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                break

            with open(file_path, "r", encoding="utf-8") as f:
                content = f"For more chapters (10+) or if you want to support me, visit https://www.patreon.com/FFAddict. Thank you!\n{f.read()}"
            if comments:
                content = f"{comments}\n\n{content}"
            try:
                upload_to_inkstone(
                    story=full_story_name,
                    chapter_title=f"Chapter {current_inkstone_chapter}",
                    content=content,
                    driver=driver,
                    in_create_page=in_create_page
                )
                current_inkstone_chapter += 1
                in_create_page = True
            except Exception as e:
                print(e)
                break
        data_json[full_story_name]["Next Inkstone Chapter"] = current_inkstone_chapter

    # Upload to Patreon if requested
    if platform in ["both", "patreon"]:
        driver.get("https://www.patreon.com/c/FFAddict")
        time.sleep(10)
        for _ in range(chapters):
            file_path = os.path.join(
                os.getcwd(), "outputs", story_name_dir, f"{current_patreon_chapter}.txt"
            )
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                break

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                upload_to_patreon(
                    category=patreon_category,
                    chapter_title=f"{full_story_name} - Chapter {current_patreon_chapter}",
                    content=content,
                    driver=driver
                )
                current_patreon_chapter += 1
            except Exception as e:
                print(e)
                break

        data_json[full_story_name]["Next Patreon Chapter"] = current_patreon_chapter
    save_json(os.path.join(os.getcwd(), 'json', 'data.json'), data_json)
    # driver.quit()


if __name__ == '__main__':
    print("Upload to Inkstone and/or Patreon")

    story_data_json = load_json(os.path.join(os.getcwd(), 'json', 'data.json'))
    storylist = list(story_data_json.keys())

    # Show list of stories
    print("Stories available:")
    for i, story in enumerate(storylist, start=1):
        print(f"{i}: {story}")

    # Option for uploading X chapters for all or for specific stories
    option = input(
        "\nSelect an option:\n"
        "1) Upload X chapters for ALL stories\n"
        "2) Upload X chapters for specific stories\n"
        "Choose: "
    ).strip()

    chapters = int(input("How many chapters to upload: "))

    # New: choose a platform
    platform_choice = input(
        "\nSelect platform:\n"
        "1) Patreon only\n"
        "2) Inkstone only\n"
        "3) Both\n"
        "Choose: "
    ).strip()

    if platform_choice == "1":
        platform = "patreon"
    elif platform_choice == "2":
        platform = "inkstone"
    elif platform_choice == "3":
        platform = "both"
    else:
        print("Invalid platform option selected.")
        platform = "both"

    comments = ""
    if platform in ["both", "inkstone"]:
        comments = input("Comments for Inkstone?:\n")

    if option == "1":
        # Upload for ALL stories
        for story in storylist:
            try:
                double_upload(chapters, story, comments, platform)
            except Exception as e:
                print("Error for patreon")
                print(e)
    elif option == "2":
        # Upload for SPECIFIC stories
        selection = input("Enter story numbers separated by space: ").split()
        for sel in selection:
            index = int(sel) - 1
            if 0 <= index < len(storylist):
                story_name = storylist[index]
                double_upload(chapters, story_name, comments, platform)
    else:
        print("Invalid option selected.")
