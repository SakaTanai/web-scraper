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
        try:
            price = price.get_text()
        except AttributeError:
            pass
        price = price_regex.sub('', price)
        price = price[:len(price) - 3]
        price = price[:len(price)-2] + ',' + price[len(price)-2:]
# Append the prices to the list.
        new_list.append(price)
    return new_list

# A function that writes the information in the lists in a CSV file.
def export(file_title, title_list, price_list):
    # Open the CSV file where the information will be exported to.
    with open(file_title, 'w', newline='') as file:
        file_name = csv.writer(file)
        for i in range(len(title_list)):
            title = title_list[i]
            price = price_list[i]
            file_name.writerow([title, price])

# A function that sorts the product titles on Evolio. The site doesn't use classes for product titles, so we cannot
# rely on the normal sorting method.
def evolio_sort(list):
    new_list = []
    for i in range(2, len(list), +3):
        new_list.append(list[i])
    return new_list

# Collect the information from the pages.
url_emag = 'https://www.emag.ro/laptopuri/sort-priceasc/p2/c'    # store the URL in a variable for easier reading
emag = requests.get(url_emag)    # collect the information from the site at the url variable

url_altex = 'https://altex.ro/laptopuri/cpl/filtru/order/price/dir/asc/p/2/'
altex = requests.get(url_altex)

url_evolio = 'https://www.evolioshop.com/ro/smartwatch.html?dir=asc&order=price'
evolio = requests.get(url_evolio)

# Create the BeautifulSoup Objects to parse the data from the page request.
soup_emag = BeautifulSoup(emag.text, 'html.parser')
soup_altex = BeautifulSoup(altex.text, 'html.parser')
soup_evolio = BeautifulSoup(evolio.text, 'html.parser')

# Get the title information for all the products on the page. This information needs to be sorted.
emag_product_titles_not_sorted = soup_emag.find_all('a', class_='product-title js-product-url')
altex_product_titles_not_sorted = soup_altex.find_all('a', class_='Product-name ')
evolio_product_titles_not_sorted = soup_evolio.find_all('h2')

# Create the list that where the product titles will be kept. This list is full of whitespaces and
# newlines that must be deleted. Hence, it is only temporary.
emag_product_titles_sorted_spaces = title_text(emag_product_titles_not_sorted)
altex_product_titles_sorted = title_text(altex_product_titles_not_sorted)
evolio_product_titles_sorted_raw = title_text(evolio_product_titles_not_sorted)

# Create another intermediary list that sorts through the raw data from Evolio.
evolio_product_titles_sorted_spaces = evolio_sort(evolio_product_titles_sorted_raw)

# Create the final list that holds titles. This list will later be exported.
emag_product_titles_sorted = format(emag_product_titles_sorted_spaces)
evolio_product_titles_sorted = format(evolio_product_titles_sorted_spaces)

# Get the price information for all the products on the page. This information is raw and needs to be filtered.
emag_product_prices = soup_emag.find_all(class_='product-new-price')
altex_product_prices = soup_altex.find_all(class_='Price-current')
evolio_product_prices_raw = soup_evolio.find_all(class_= re.compile("price special-price product-price"))

# Use the function that sorts titles in order to sort the prices in the same manner. Then, use the function that
# formats titles in order to format the price.
evolio_product_prices_spaces = title_text(evolio_product_prices_raw)
evolio_product_prices = format(evolio_product_prices_spaces)

# Create the list that will hold the prices.
emag_price_list = price_filter(emag_product_prices)
altex_price_list = price_filter(altex_product_prices)
evolio_price_list = price_filter(evolio_product_prices)

# Call the function to export the information from the lists into a CSV file.
export('products_emag.csv', emag_product_titles_sorted, emag_price_list)
export('products_altex.csv', altex_product_titles_sorted, altex_price_list)
export('products_evolio.csv', evolio_product_titles_sorted, evolio_price_list)

"""
with open('products_altex.csv', 'r') as altex_file_raw:
    altex_file = csv.reader(altex_file_raw)
    for row_altex in altex_file:
        with open('products_emag.csv', 'r') as file:
            emag_file = csv.reader(file)
            for row_emag in emag_file:
                print(row_altex)
"""



"""
TO DO:
1) Export the lists to a file and start working with that file. (Export done. See how to work with info directly from
   the file. - see https://realpython.com/python-csv/)
2) Write the code for getting data from other sites as well. (half-done)
3) Try and compare the products from different sites. Just compare the prices, to see if it works.
4) Follow the TO DO in the readme for further instructions.
"""