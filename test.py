import requests
from bs4 import BeautifulSoup
import requests

url = 'http://www.j-archive.com/showgame.php?game_id=6531'
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')
if (soup.find(class_="error")):
    print('Error')
else:
    print(soup)