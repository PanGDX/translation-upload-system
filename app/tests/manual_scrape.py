import sys
import os

# Ensure the app directory is in the python path
sys.path.append(os.getcwd())

from app.models import Raw_Chapter
from app.utils.scrape import Scraper_Unit



def manual_test_scrape():
    print("--- Starting Manual Scraper Test ---\n")
    
    start_url = str(input("TEST URL:"))
    scraper = Scraper_Unit(start_url)

    print("[MODE] REAL NETWORK & AI (Costs Tokens!)")

    
    # You might want to change the URL to a real one for this to work
    print(f"Targeting: {scraper.url}")
    execute_logic(scraper)


def execute_logic(scraper: Scraper_Unit):
    """
    The core logic we want to test
    """
    # TEST 1: SCRAPING
    print("\n1. Testing scrape_unit()...")
    try:
        chapter_obj = scraper.scrape_unit()
        
        print("\n   [SUCCESS] Object Created:")
        print(f"   Title: {chapter_obj.title}")
        print(f"   Chapter Num: {chapter_obj.chapter_number}")
        print(f"   URL: {chapter_obj.url}")
        print(f"   Content Preview: {chapter_obj.content[:50]}...")
        
        if isinstance(chapter_obj, Raw_Chapter):
            print("   Type Check: Valid Raw_Chapter Pydantic Model")
        else:
            print("   Type Check: FAILED")

    except Exception as e:
        print(f"   [ERROR] Scraping failed: {e}")
        import traceback
        traceback.print_exc()

    # TEST 2: NAVIGATION
    print("\n2. Testing go_to_next_link()...")
    try:
        # Force the scraper to not know the identifier initially
        scraper._next_link_identifier = [] 
        
        success = scraper.go_to_next_link(attempt_detection=True)
        
        if success:
            print(f"   [SUCCESS] Navigated to: {scraper.url}")
            print(f"   Identified Link Selector: {scraper._next_link_identifier}")
        else:
            print("   [FAILURE] Could not navigate.")

    except Exception as e:
        print(f"   [ERROR] Navigation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    manual_test_scrape()