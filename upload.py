from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

chromedriver_path = "chromedriver.exe"
chrome_options = Options()
chrome_options.add_argument("user-data-dir=C:\\Users\\User\\AppData\\Local\\Google\\Chrome\\User Data")
driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)


# driver.get("https://www.patreon.com/FFAddict")
driver.get("https://inkstone.webnovel.com/novels/list?story=1")

def upload_to_patreon(category:str, title:str, content:str):

    button_xpath = "//button[contains(., 'Create')]"
    button_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, button_xpath))
    )
    button_element.click()

    text_upload_xpath = "//a[contains(., 'Text') and @id = 'post_type_link_text_only']"
    text_upload_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, text_upload_xpath))
    )
    text_upload_element.click()


    title_input_xpath = "//input[@placeholder='Add a title']"
    title_input_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, title_input_xpath))
    )
    title_input_element.send_keys(title)


    body_input_xpath = "//div[@contenteditable='true' and @class='ProseMirror remirror-editor']"
    body_input_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, body_input_xpath))
    )
    body_input_element.send_keys(content)

    category_access_xpath = "//button[@id='collections-list-dropdown']"
    category_access_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, category_access_xpath))
    )
    category_access_element.click()

    category_access_xpath = f"//li[contains(., '{category}')]"
    category_access_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, category_access_xpath))
    )
    category_access_element.click()

    next_button_xpath = f"//button[contains(., 'Next') and @type='button']"
    next_button_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, next_button_xpath))
    )
    next_button_element.click()

    sale_button_xpath = f"//button[@id='sell-post-toggle' and @role='switch']"
    sale_button_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, sale_button_xpath))
    )
    sale_button_element.click()

    publish_button_xpath = f"//button[contains(., 'Publish') and @type='button']"
    publish_button_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, publish_button_xpath))
    )
    publish_button_element.click()


    share_button_xpath = f"//button[@aria-label='Close the share dialog']"
    share_button_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, share_button_xpath))
    )
    share_button_element.click()

def upload_to_inkstone(story:str, title:str, content:str, inCreatePage:bool = False):
    if(not inCreatePage):
        story_div_xpath = f"//tr[contains(., '{story}')]"
        story_div_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, story_div_xpath))
        )
        
        explore_button_xpath = ".//button[@data-report-uiname='explore']"
        explore_button = story_div_element.find_element(By.XPATH, explore_button_xpath)
        explore_button.click()

    create_button_xpath = f"//button[contains(., 'CREATE CHAPTER')]"
    create_button_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, create_button_xpath))
    )
    create_button_element.click()

    time.sleep(2)
    title_input_xpath = f"//input[@type='text' and @placeholder='Title Here']"
    title_input_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, title_input_xpath))
    )
    title_input_element.send_keys(title)

    div_xpath = f"//div[contains(@class, 'tox-edit-area')]//iframe"
    iframe_element = driver.find_element(By.XPATH, div_xpath)
    driver.switch_to.frame(iframe_element)

    body_input_xpath = f"//body[@id='tinymce' and @contenteditable='true']"
    body_input_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, body_input_xpath))
    )
    body_input_element.send_keys(content)

    driver.switch_to.default_content()

# test
    title_input_xpath = f"//input[@type='text' and @placeholder='Title Here']"
    title_input_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, title_input_xpath))
    )
    title_input_element.send_keys(title)


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
try:
    upload_to_inkstone("Harry Potter: Please Graduate From Hogwarts Soon and Go Away!", "Aplha", "asdw")
except Exception as e:
    print(e)
input()