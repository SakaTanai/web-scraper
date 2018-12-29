# Import the libraries that we are going to use for scraping the web.
import requests, re
from bs4 import BeautifulSoup

# Collect the information from the page.
url = 'https://www.emag.ro/laptopuri/sort-priceasc/p2/c'    # store the URL in a variable for easier reading
page = requests.get(url)    # collect the information from the site at the url variable

# Create a BeautifulSoup Object to parse the data from the page request.
soup = BeautifulSoup(page.text, 'html.parser')

# Continue with the project:
# https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3

# Get the title information for all the products on the page. This information needs to be sorted.
product_titles_not_sorted = soup.find_all('a', class_='product-title js-product-url')

# Sort the information and save it in a list.
for product in product_titles_not_sorted:
    for title in product.descendants:
        print(title)
