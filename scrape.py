from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from utility import add_story


def scrape():
    full_story_name = str(input("Full story name: "))
    patreon_story_name = str(input("Patreon Category name: "))

    output_folder_name = add_story(full_story_name, patreon_story_name)

    current_chapter_number = int(input("Chapter number: "))
    url_to_scrape = str(input("URL of the chapter: "))
    content_text = str(input(
        "A part of the content of the chapter (copy a small part of the content): "))
    link_text = str(input(
        "The text on the button leading to the next chapter (multiple = separated by space): "))

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(
        "user-data-dir=C:\\Users\\User\\AppData\\Local\\Google\\Chrome\\User Data")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("Driver is running")

    driver.get(url_to_scrape)

    def url_formatting(url, next_link):
        """
        Format the URL based on whether the next link is a full URL or a relative path.
        """
        if "http" in next_link:
            return next_link
        else:
            bracket_position = url.find("/", url.find("//") + 2)
            return url[:bracket_position] + next_link

    def find_divs_with_text():
        """
        Find the divs that contain the specified content text and extract their class and ID.
        """
        search_text = content_text.strip()
        xpath_expression = f"//div[contains(., '{search_text}')]"
        div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_expression))
        )
        tag_class = div.get_attribute("class")
        tag_id = div.get_attribute("id")

        print(f"DIV ID: {tag_id} Class: {tag_class}")

        return tag_class.strip(), tag_id.strip()

    def get_link():
        """
        Get the link for the next chapter by finding 'a' tags containing the specified link text.
        """
        text = link_text.lower().split(" ")
        for search_text in text:
            if search_text:
                xpath_expression = f"//a[contains(., '{search_text}')]"
                matched_tags = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, xpath_expression))
                )
                href = matched_tags.get_attribute("href")
                return href

        raise ValueError(
            "Failed to fetch the link with the given class names or link text. Possibly due to the end")

    def scrape_webpage(url, counter):
        """
        Scrape the webpage content and navigate to the next chapter based on the link.
        """
        try:
            driver.get(url)

            if content_class and content_id:
                xpath_expression = f"//div[@class='{content_class}' and @id='{content_id}']"
            elif content_class:
                xpath_expression = f"//div[@class='{content_class}']"
            elif content_id:
                xpath_expression = f"//div[@id='{content_id}']"
            else:
                raise ValueError("No class or id!")

            contents = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath_expression))
            )
            content = "\n".join([element.text for element in contents])

            with open(f"{os.getcwd()}/inputs/{output_folder_name}/{counter}.txt", "w", encoding="utf-8") as file:
                file.write(content)

            next_link = get_link()
            if next_link:
                print(f"Navigating to the next link: {next_link}")
                scrape_webpage(url_formatting(url, next_link), counter + 1)
            else:
                print("No next link found, or there was an error fetching it.")
        except Exception as e:
            print(f"An error occurred: {e}")

    try:
        content_class, content_id = find_divs_with_text()
        scrape_webpage(url_to_scrape, current_chapter_number)
    finally:
        driver.quit()
