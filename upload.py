from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from utility import setup_chrome_driver, load_json


def upload_to_patreon(category: str, chapter_title: str, content: str, driver: webdriver.Chrome):
    """
    ### @param category: the category name in the drop down list
    ### @param title: the title of the current chapter - story name + current chapter count
    ### @param content: the content
    ### @param driver: Chrome driver

    The function that will submit to the Patreon website and return to the homepage of Patreon
    """

    button_xpath = "//button[contains(., 'Create')]"
    button_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, button_xpath))
    )
    button_element.click()

    text_upload_xpath = "//a[contains(., 'Text') and ### @id = 'post_type_link_text_only']"
    text_upload_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, text_upload_xpath))
    )
    text_upload_element.click()

    title_input_xpath = "//input[### @placeholder='Add a title']"
    title_input_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, title_input_xpath))
    )
    title_input_element.send_keys(chapter_title)

    body_input_xpath = "//div[### @contenteditable='true' and ### @class='ProseMirror remirror-editor']"
    body_input_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, body_input_xpath))
    )
    body_input_element.send_keys(content)

    category_access_xpath = "//button[### @id='collections-list-dropdown']"
    category_access_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, category_access_xpath))
    )
    category_access_element.click()

    category_access_xpath = f"//li[contains(., '{category}')]"
    category_access_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, category_access_xpath))
    )
    category_access_element.click()

    next_button_xpath = f"//button[contains(., 'Next') and ### @type='button']"
    next_button_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, next_button_xpath))
    )
    next_button_element.click()

    sale_button_xpath = f"//button[### @id='sell-post-toggle' and ### @role='switch']"
    sale_button_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, sale_button_xpath))
    )
    sale_button_element.click()

    publish_button_xpath = f"//button[contains(., 'Publish') and ### @type='button']"
    publish_button_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, publish_button_xpath))
    )
    publish_button_element.click()

    share_button_xpath = f"//button[### @aria-label='Close the share dialog']"
    share_button_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, share_button_xpath))
    )
    share_button_element.click()


def upload_to_inkstone(story: str, chapter_title: str, content: str, driver: webdriver.Chrome, in_create_page: bool = False):
    """
    ### @param story: the category name in the directory list
    ### @param title: the title of the current chapter - story name + current chapter count
    ### @param content: the content
    ### @param driver: Chrome driver
    ### @in_create_page: is the current page the create page or the directory page 
    The function that will submit to the Patreon website and return to the homepage of Patreon
    """

    if (not in_create_page):
        story_div_xpath = f"//tr[contains(., '{story}')]"
        story_div_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, story_div_xpath))
        )

        explore_button_xpath = ".//button[### @data-report-uiname='explore']"
        explore_button = story_div_element.find_element(
            By.XPATH, explore_button_xpath)
        explore_button.click()

    create_button_xpath = f"//button[contains(., 'CREATE CHAPTER')]"
    create_button_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, create_button_xpath))
    )
    create_button_element.click()

    time.sleep(2)
    title_input_xpath = f"//input[### @type='text' and ### @placeholder='Title Here']"
    title_input_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, title_input_xpath))
    )
    title_input_element.send_keys(chapter_title)

    div_xpath = f"//div[contains(### @class, 'tox-edit-area')]//iframe"
    iframe_element = driver.find_element(By.XPATH, div_xpath)
    driver.switch_to.frame(iframe_element)

    body_input_xpath = f"//body[### @id='tinymce' and ### @contenteditable='true']"
    body_input_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, body_input_xpath))
    )
    body_input_element.send_keys(content)

    driver.switch_to.default_content()

    title_input_xpath = f"//input[### @type='text' and ### @placeholder='Title Here']"
    title_input_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, title_input_xpath))
    )
    title_input_element.send_keys(chapter_title)

    publish_button_xpath = "//button[span[contains(., 'Publish')]]"
    publish_button_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, publish_button_xpath))
    )
    publish_button_element.click()

    confirm_button_xpath = f"//button[contains(., 'confirm')]"
    confirm_button_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, confirm_button_xpath))
    )
    confirm_button_element.click()


def double_upload(chapters: int, full_story_name: str):
    """
    ### @param chapters: the number of chapters to upload
    """

    driver = setup_chrome_driver()

    data = load_json(os.path.join(os.getcwd(), 'json', 'data.json'))
    assert (full_story_name in data)
    data = data[full_story_name]
    patreon_category = data["Patreon Category"]
    current_inkstone_chapter = data["Next Inkstone Chapter"]
    current_patreon_chapter = data["Next Patreon Chapter"]

    for _ in range(chapters):
        content = open(
            os.path.join(os.getcwd(), "outputs", full_story_name, f"{current_inkstone_chapter}.txt"),
            "r",
            encoding="utf-8").read()
        
        upload_to_inkstone(
            story=full_story_name,
            chapter_title=f"Chapter {current_inkstone_chapter}",
            content= content,
            driver=driver,
            in_create_page=False
        )
        current_inkstone_chapter += 1
    for _ in range(chapters):
        content = open(
            os.path.join(os.getcwd(), "outputs", full_story_name, f"{current_patreon_chapter}.txt"),
            "r",
            encoding="utf-8").read()

        upload_to_patreon(
            category=patreon_category,
            chapter_title=f"{full_story_name} - Chapter {current_patreon_chapter}",
            content= content,
            driver=driver
        )
        current_patreon_chapter += 1


    data["Next Inkstone Chapter"] = current_inkstone_chapter
    data["Next Patreon Chapter"] = current_patreon_chapter



if __name__ == '__main__':
    print("Upload to inkstone and patreon")
    
    story_data_json = load_json(os.path.join(os.getcwd(), 'json', 'data.json'))
    storylist = list(story_data_json.keys())

    for i, story in enumerate(storylist, 1):
        print(f"{i}: {story}")
    story_name = storylist[int(input("Choose: ")) - 1]   
    chapters = int(input("How many chapters to upload: "))
    double_upload(chapters, story_name)