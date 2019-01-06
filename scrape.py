# Import the libraries that we are going to use for scraping the web.
import requests, re, csv
from bs4 import BeautifulSoup

# Create the regex that will be used for deleting unnecessary formatting from the list.
price_regex = re.compile(r'\W')

# A function to remove whitespaces from a list. It returns a well formatted list, without newlines or unnecessary
# whitespaces.
def format(list):
    list_sorted = []
    for title in list:
        new_title = title.replace('\n', '')
        new_title = new_title.lstrip()
        new_title = new_title.rstrip()
        list_sorted.append(new_title)
    return list_sorted

# A function that gets the title information with tags and returns just the text.
def title_text(list):
    new_list = []
    for product in list:
        for title in product.descendants:
            new_list.append(title)
    return new_list

# A function that filters the price information for prices from the site:
def price_filter(list):
    new_list = []
    for product in list:
# Create a price backup so as not to mess with the iterator. Then eliminate the information held between the 'span'
# tags. We only need the numbers for the prices.
        price = product
# Get the prices and format them nicely.
        price = price.get_text()
        price = price_regex.sub('', price)
        price = price[:len(price) - 3]
        price = price[:len(price)-2] + ',' + price[len(price)-2:]
# Append the prices to the list.
        new_list.append(price)
    return new_list

# A function that writes the information in the lists in a CSV file.
def export(title_list, price_list, file_name):
    for i in range(len(title_list)):
        title = title_list[i]
        price = price_list[i]
        file_name.writerow([title, price])

# Collect the information from the pages.
url_emag = 'https://www.emag.ro/laptopuri/sort-priceasc/p2/c'    # store the URL in a variable for easier reading
emag = requests.get(url_emag)    # collect the information from the site at the url variable

url_altex = 'https://altex.ro/laptopuri/cpl/filtru/order/price/dir/asc/p/2/'
altex = requests.get(url_altex)

# Create the BeautifulSoup Objects to parse the data from the page request.
soup_emag = BeautifulSoup(emag.text, 'html.parser')
soup_altex = BeautifulSoup(altex.text, 'html.parser')

# Get the title information for all the products on the page. This information needs to be sorted.
emag_product_titles_not_sorted = soup_emag.find_all('a', class_='product-title js-product-url')
altex_product_titles_not_sorted = soup_altex.find_all('a', class_='Product-name ')

# Create the list that where the product titles will be kept. This list is full of whitespaces and
# newlines that must be deleted. Hence, it is only temporary.
emag_product_titles_sorted_spaces = title_text(emag_product_titles_not_sorted)
altex_product_titles_sorted = title_text(altex_product_titles_not_sorted)

# Create the final list that holds titles. This list will later be exported.
emag_product_titles_sorted = format(emag_product_titles_sorted_spaces)

# Get the price information for all the products on the page. This information is raw and needs to be filtered.
emag_product_prices = soup_emag.find_all(class_='product-new-price')
altex_product_prices = soup_altex.find_all(class_='Price-current')

# Create the list that will hold the prices.
emag_price_list = price_filter(emag_product_prices)
altex_price_list = price_filter(altex_product_prices)

# Open the CSV file where the information will be exported to.
with open('products_emag.csv', 'w', newline = '') as file:
    emag_file = csv.writer(file)
# Export the list information into the CSV file.
    export(emag_product_titles_sorted, emag_price_list, emag_file)

with open('products_altex.csv', 'w', newline = '') as file:
    altex_file = csv.writer(file)
    export(altex_product_titles_sorted, altex_price_list, altex_file)

with open('products_altex.csv', 'r') as file:
    altex_file = csv.reader(file)
    for row in altex_file:
        print(row)

with open('products_emag.csv', 'r') as file:
    emag_file = csv.reader(file)
    for row in emag_file:
        print(row)

"""
TO DO:
1) Export the lists to a file and start working with that file. (Export done. See how to work with info directly from
   the file. - see https://realpython.com/python-csv/)
2) Write the code for getting data from other sites as well. (half-done)
3) Try and compare the products from different sites. Just compare the prices, to see if it works.
4) Follow the TO DO in the readme for further instructions.
"""