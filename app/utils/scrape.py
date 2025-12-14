from urllib.parse import urlparse, urljoin
from urllib.error import URLError
import requests
from bs4 import BeautifulSoup
import json

# Assuming these imports exist in your project structure
from app.models import Input_Query, Output_Response, Raw_Chapter
from app.utils.ai_calling import ai_request

class Scraper_Unit:
    """
    Scraper_Unit
    - set url
    - get next link navigation method
    - go to next link
    - scrape and clean using AI: out as Raw_Chapter
    """
    def __init__(self, url):
        self._url: str = url
        # We store identifiers as a list to try multiple known strategies (e.g., "Next", "Next Chapter", ">")
        self._next_link_identifier: list[str] = [] 
        self._session = requests.Session() # Use session for cookie persistence
        
        # Validate initial URL
        self.url = url 

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url_string):
        try:
            result = urlparse(url_string)
            if all([result.scheme, result.netloc]):
                self._url = url_string
            else:
                raise ValueError("Invalid URL scheme")
        except (AttributeError, ValueError):
            raise URLError(f"Invalid URL provided: {url_string}")

    def _fetch_page(self):
        """Helper to get page content securely"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = self._session.get(self._url, headers=headers, timeout=10)
            
            response.encoding = response.apparent_encoding 

            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {self._url}: {e}")
            return None

    def go_to_next_link(self, attempt_detection=True) -> bool:
        """
        Attempts to find the next link using stored identifiers.
        If not found and attempt_detection is True, runs AI detection and retries.
        """
        soup = self._fetch_page()
        if not soup:
            return False

        # 1. Try to find link with existing identifiers
        next_url = None
        
        # Priority: Check exact text match, then partial text, then class/id
        for identifier in self._next_link_identifier:
            # Check by Text
            link = soup.find('a', string=lambda text: text and identifier.lower() in text.lower())
            if not link:
                # Check by Class or ID
                link = soup.find('a', class_=identifier) or soup.find('a', id=identifier)
            
            if link and link.get('href'):
                next_url = link.get('href')
                break

        # 2. If found, update URL and return Success
        if next_url:
            # Handle relative URLs (e.g., "/chapter-2")
            self.url = urljoin(self._url, next_url)
            print(f"Navigated to: {self._url}")
            return True

        # 3. If NOT found, use AI to find the identifier (only once)
        if attempt_detection:
            print(f"Next button not found with {self._next_link_identifier}. Asking AI...")
            new_identifier = self.get_next_link_identifier(soup)
            
            if new_identifier:
                self._next_link_identifier.append(new_identifier)
                # Recursively try again, but set attempt_detection=False to prevent infinite loop
                return self.go_to_next_link(attempt_detection=False)
        
        print("Failed to find next link.")
        return False

    def get_next_link_identifier(self, soup=None) -> str:
        """
        Extracts all <a> tags, filters for likely candidates, and asks AI 
        to identify the text/class of the 'Next' button.
        """
        if not soup:
            soup = self._fetch_page()

        # 1. Scrape likely candidates to save token costs
        # We don't send the whole HTML. We send a list of links.
        candidates = []
        for a in soup.find_all('a', href=True):
            text = a.get_text(strip=True)
            # Heuristic: Next buttons are usually short or contain "next"
            if text and (len(text) < 30 or "next" in text.lower() or ">" in text):
                candidates.append({
                    "text": text,
                    "class": a.get('class'),
                    "id": a.get('id'),
                    "href": a.get('href')
                })

        if not candidates:
            return ""

        # 2. Construct AI Query
        prompt_content = f"""
        I am scraping a novel. Here is a list of links found on the page. 
        Identify which one is the "Next Chapter" button.
        
        Candidates: {json.dumps(candidates[:20])}""".strip()

        system_prompt = """
        Return ONLY the JSON object with the field 'response'. 
        The 'response' should be the visible text (preferred) or the unique class name.
        Example: {{"response": "Next Chapter"}}""".strip()

        print("Logging: Sent to AI - find next button")
        query = Input_Query(
            type="Coding", # Using 'Coding' temp (0.0) for precision
            system_prompt=system_prompt,
            user_query=prompt_content
        )
        
        # 3. AI Request
        try:
            response_obj:Output_Response = ai_request(query) 
            # Assuming output_response has a 'content' dict or similar. 
            # Adjust based on your actual Output_Response model structure.
            # Here I assume the AI returns a dict matching the structure requested.
            print(f"Logging: {response_obj=}")
            identifier = response_obj.response
            print(f"AI identified next button as: {identifier}")
            return identifier
        except Exception as e:
            print(f"AI Detection failed: {e}")
            return ""

    def scrape_unit(self) -> Raw_Chapter:
        """
        Scrapes the current page and uses AI to clean it.
        """
        soup = self._fetch_page()
        if not soup:
            raise URLError("Could not fetch page to scrape")

        # Get main text (strip scripts and styles)
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        raw_text = soup.get_text(separator="\n")[:10000] # Limit tokens
        print(f"Log: {raw_text=}")
        system_prompt = f"""
        Extract the novel chapter from this raw text.
        1. Identify the Chapter Number (integer).
        2. Identify the Chapter Title.
        3. Clean the body content (remove menu text, ads, 'prev/next' text).

        Return JSON containing: "chapter_number", "content", "title"
        """

        user_prompt = f"""
        Raw Text:
        {raw_text}
        """

        query = Input_Query(
            type="Data Cleaning",
            system_prompt=system_prompt,
            user_query=user_prompt
        )

        print("Log: Sending to AI")
        response_obj = ai_request(query)
        
        # Use Pydantic model_validate to convert dict to Raw_Chapter object
        # Ensure your AI response returns keys: 'chapter_number', 'title', 'content', 'url'
        chapter_data = response_obj # Or response_obj.dict() depending on implementation
        chapter_data['url'] = self._url
        
        return Raw_Chapter.model_validate(chapter_data)