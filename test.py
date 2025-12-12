import requests
from bs4 import BeautifulSoup

url = "https://www.google.com/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

for a_tag in soup.find_all('a'):
    print(f"{a_tag=}")
    for i in a_tag.parents:
        print(i)
    
    print("\n\n\n\n")