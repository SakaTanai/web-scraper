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

# Create the list that where the product titles will be kept. This list is full of whitespaces and
# newlines that must be deleted. Hence, it is only temporary.
product_titles_sorted_spaces = []

# Sort the information and save it in a list.
for product in product_titles_not_sorted:
    for title in product.descendants:
        product_titles_sorted_spaces.append(title)

# Create the final list that holds titles. This list will later be exported.
product_titles_sorted = []

# Remove whitespaces from the list. Each new_title iteration is the last new_title iteration + an additional change.
for title in product_titles_sorted_spaces:
    new_title_1 = title.replace('\n', '')
    new_title_2 = new_title_1.lstrip()
    new_title_3 = new_title_2.rstrip()
    product_titles_sorted.append(new_title_3)


# Get the price information for all the products on the page. This information is raw and needs to be filtered.
product_prices = soup.find_all(class_="product-new-price")

# Create the list that will hold the prices.
price_list = []

# Create the regex that will be used for deleting unnecessary formatting from the list.
price_regex = re.compile(r'\W')

# Filter the information:
for product in product_prices:
# Create a price backup so as not to mess with the iterator. Then eliminate the information held between the 'span'
# tags. We only need the numbers for the prices.
    price = product
    try:
        price.find('span').decompose()
    except AttributeError:
        continue
# Get the prices and format them nicely.
    price = price.get_text()
    price = price_regex.sub('', price)
    price = price[:len(price)-2] + ',' + price[len(price)-2:]
# Append the prices to the list.
    price_list.append(price)

print(price_list)

"""
TO DO:

1) See if X.get_text() works on the item titles. This can save a ton of space.
2) First optimisation steps: create functions for similar code blocks.
3) Export the lists to a file and start working with that file.
4) Write the code for getting data from other sites as well.
5) Try and compare the products from different sites. Just compare the prices, to see if it works.
6) Follow the TO DO in the readme for further instructions.
"""