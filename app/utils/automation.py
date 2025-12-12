import yaml
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BrowserManager:
    def __init__(self, driver, config_path="selectors.yaml"):
        self.driver = driver
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

    def _get_locator(self, platform, element_name):
        """Helper to fetch xpath from yaml"""
        try:
            # Navigate nested dict: platform -> create_flow -> element
            if 'create_flow' in self.config[platform] and element_name in self.config[platform]['create_flow']:
                data = self.config[platform]['create_flow'][element_name]
            else:
                data = self.config[platform][element_name]
            
            return (By.XPATH, data['xpath'])
        except KeyError:
            raise Exception(f"Selector '{element_name}' not found in YAML for {platform}")

    def click(self, platform, element_name, dynamic_text=None):
        """Finds an element and clicks it."""
        locator_strategy, locator_value = self._get_locator(platform, element_name)
        
        if dynamic_text:
            locator_value = locator_value.replace("{REPLACE}", dynamic_text)

        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((locator_strategy, locator_value))
        )
        element.click()
        time.sleep(1) # Small buffer for UI animations

    def input_text(self, platform, element_name, text):
        """Finds an input and sends keys."""
        locator = self._get_locator(platform, element_name)
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(locator)
        )
        element.send_keys(text)

    def get_text(self, platform, element_name):
        """Gets text from an element."""
        locator = self._get_locator(platform, element_name)
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(locator)
        )
        return element.text

    def switch_to_frame(self, platform, element_name):
        """Switches driver context to an iframe."""
        locator = self._get_locator(platform, element_name)
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(locator)
        )
        self.driver.switch_to.frame(iframe)

    def switch_to_default(self):
        self.driver.switch_to.default_content()