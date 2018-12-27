# Import the libraries that we are going to use for scraping the web.
import requests
from bs4 import BeautifulSoup

# Collect the information from the page.
url = 'https://www.emag.ro/laptopuri/sort-priceasc/p2/c'    # store the URL in a variable for easier reading
page = requests.get(url)    # collect the information from the site at the url variable

# Create a BeautifulSoup Object to parse the data from the pag request.
soup = BeautifulSoup(page.txt, 'html.parser')

# Continue with the project:
https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3


