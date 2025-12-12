"""
Status: Working

An automated scraping program that runs in the background, using Selenium.
This program does not work on websites with Captcha.
This program occasionally fails. This is inevitable due to the nature of websites haivng a great deal of variance

Minimised error occurrence by scraping with XML and then BS4.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
import os
import time
import random
from old.utility import add_story, setup_chrome_driver
import traceback
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup


def url_formatting(url: str, next_link: str) -> str:
	"""
	### @param url: The current url
	### @param next_link: The next link
	### @return: The full URL with https of the next chapter

	Format the URL based on whether the next link is a full URL or a relative path.
	"""
	if "http" in next_link:
		return next_link
	else:
		# Handle relative URLs
		base_url = url[:url.find("/", url.find("//") + 2)]
		return base_url + next_link


def find_divs_with_text(content_text: str, driver: webdriver.Chrome) -> tuple[str, str]:
	"""
	### @param content_text: the specified content text
	### @param driver: Chrome Driver

	Find the div that contains the specified content text and extract its class and ID.

	"""
	search_text: str = content_text.strip()
	xpath_expression: str = f"//div[contains(., '{search_text}')]"
	try:
		div = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.XPATH, xpath_expression))
		)
		tag_class: str = div.get_attribute("class") or ""
		tag_id: str = div.get_attribute("id") or ""

		print(f"Found content div - ID: '{tag_id}', Class: '{tag_class}'")
		return tag_class.strip(), tag_id.strip()
	except TimeoutException:
		page_source = driver.page_source
		soup = BeautifulSoup(page_source, "html.parser")
		divs = soup.find_all(lambda tag: tag.name ==
							"div" and search_text in tag.get_text(strip=True))
		if divs:
			div = divs[0]
			tag_class = " ".join(div.get("class", [])) if div.get("class") else ""
			tag_id = div.get("id", "")
			print(
				f"Found content div using fallback - ID: '{tag_id}', Class: '{tag_class}'")
			return tag_class.strip(), tag_id.strip()
		else:
			raise TimeoutException(
				"Timeout: Could not find the div containing the specified content text using both Selenium and BeautifulSoup."
			)

	except Exception as e:
		print(traceback.format_exc())
		print(f"Unexpected error: {e}")
		raise


def get_link(link_text: str, driver: webdriver.Chrome) -> str:
	"""
	### @param link_text: the text leading to the next chapter (such as 'Next')
	### @param driver: Chrome Driver
	### @return: the next chapter link

	Get the link for the next chapter by finding 'a' tags containing the specified link text.
	"""
	texts = link_text.lower().split(" ")
	for search_text in texts:
		search_text = search_text.strip()
		if search_text:
			xpath_expression = f"//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{search_text}')]"
			try:
				matched_tag = WebDriverWait(driver, 10).until(
					EC.presence_of_element_located(
						(By.XPATH, xpath_expression))
				)
				href = matched_tag.get_attribute("href")
				actions = ActionChains(driver)
				actions.move_to_element(matched_tag)
				if href:
					return href
			except TimeoutException:
				print(
					f"No link found with text '{search_text}'. Trying next option.")
				continue
			except Exception as e:
				print(traceback.format_exc())
				print(f"Error finding link with text '{search_text}': {e}")
				continue

	raise ValueError(
		"Failed to fetch the next chapter link with the given link text. Possibly at the end of chapters.")


def scrape(double_count:bool):
	"""
	The primary function to be called
	"""
	full_story_name: str = input("Full story name: ").strip()
	patreon_story_name: str = input("Patreon Category name: ").strip()

	try:
		output_folder_name: str = add_story(
			full_story_name, patreon_story_name)
	except Exception as e:
		print(f"Error creating output folder: {e}")
		return

	try:
		current_chapter_number: int = int(input("Chapter number: ").strip())
	except ValueError:
		print("Invalid chapter number. Please enter an integer.")
		return

	try:
		no_of_chapters_to_scrape: int = int(
			input("No of chapters to scrape: ").strip())
	except ValueError:
		print("Invalid chapter number. Please enter an integer.")
		return

	url_to_scrape: str = input("URL of the chapter: ").strip()
	if not url_to_scrape.startswith("http"):
		print("Invalid URL. Please enter a valid URL starting with http or https.")
		return

	content_text: str = input(
		"A part of the content of the chapter (copy a small part of the content): ").strip()
	link_text: str = input(
		"The text on the button leading to the next chapter (multiple words separated by space): ").strip()

	# Set up the Chrome driver
	try:
		is_headless = str(input("Headless (y/n): "))
		if is_headless == 'y':
			is_headless = True
		else:
			is_headless = False
		driver = setup_chrome_driver(is_headless)
	except Exception as e:
		print(f"Error setting up Chrome driver: {e}")
		return

	print("Driver is running")
	driver.get(url_to_scrape)

	try:
		content_class, content_id = find_divs_with_text(
			content_text, driver=driver)
	except Exception as e:
		print(f"An error occurred during scraping: {e}")
		return

	if content_class and content_id:
		xpath_expression = f"//div[@class='{content_class}' and @id='{content_id}']"
	elif content_class:
		xpath_expression = f"//div[@class='{content_class}']"
	elif content_id:
		xpath_expression = f"//div[@id='{content_id}']"
	else:
		raise ValueError("No class or id found for content div.")
	# Determine the XPath expression based on available class and ID

	url = url_to_scrape
	counter = current_chapter_number

	output_dir = os.path.join(os.getcwd(), "inputs", output_folder_name)
	os.makedirs(output_dir, exist_ok=True)
	skip_counter = True

	while no_of_chapters_to_scrape != 0:
		no_of_chapters_to_scrape -= 1
		try:
			driver.get(url)

			# Fetch all elements matching the XPath expression
			contents = WebDriverWait(driver, 10).until(
				EC.presence_of_all_elements_located(
					(By.XPATH, xpath_expression))
			)

			if not contents:
				print(f"No content found on page {url}")
				break

			content = "\n".join([element.text for element in contents])

			# Save the content to a file

			output_file_path = os.path.join(output_dir, f"{counter}.txt")

			if double_count:
				with open(output_file_path, "a", encoding="utf-8") as file:
					file.write(content)
			else:
				with open(output_file_path, "w", encoding="utf-8") as file:
					file.write(content)

			print(f"Chapter {counter} saved to {output_file_path}")

			# Attempt to find and navigate to the next chapter link
			try:

				time.sleep(random.uniform(0.7, 1))
				next_link = get_link(link_text, driver)
				if next_link:
					url = url_formatting(url, next_link)

					if double_count:
						if not skip_counter:
							counter += 1
						skip_counter = not skip_counter
					else:
						counter += 1
					print(f"Navigating to the next link: {url}")
				else:
					print("No next link found, or there was an error fetching it.")
					break  # Exit the loop if no next link is found
			except ValueError as ve:
				print(ve)
				break  # Exit the loop on ValueError
			except Exception as e:
				print(f"Error getting next link: {e}")
				break  # Exit the loop on general exception
		except TimeoutException as te:
			print(f"Timeout while scraping page {url}: {te}")
			break  # Exit the loop on timeout
		except Exception as e:
			print(f"An error occurred while scraping the webpage: {e}")
			break  # Exit the loop on general exception

	driver.quit()


if __name__ == '__main__':
	
	double_count = False
	if(str(input("Double count? (y/n): "))) == 'y':
		double_count = True
	scrape(double_count)
