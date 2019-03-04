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
    with open(file_title, 'w+', newline='') as file:
        file_name = csv.writer(file)
        for i in range(len(title_list)):
            title = title_list[i]
            price = price_list[i]
            file_name.writerow([title, price])

# A function that sorts the product titles on Evolio. The site doesn't use classes for product titles, so we cannot
# rely on the normal sorting method.
def evolio_sort(list):
    new_list = []
    for i in range(2, len(list), 2):
        new_list.append(list[i])
    return new_list

# A function that sorts the product titles on Flanco. The normal sorting function doesn't work for this site.
# We'll write a function similar to evolio_sort.
def flanco_sort_titles(list):
    new_list = []
    for i in range(1, len(list), 2):
        new_list.append(list[i])
    return new_list

# A function that pulls the right product prices from Flanco. This function will put all the price information into
# a single list. We will then sort that list and only keep the numerical values in our final list.
def flanco_sort_prices(list):
    new_list = []
    for raw_prices in list:
        prices = raw_prices.find_all(class_='price')
        for price_unfiltered in prices:
            for price_to_sort in price_unfiltered.descendants:
                new_list.append(price_to_sort)
    return new_list

# A function that filters the raw prices pulled by the function above.
def flanco_price_filter(list):
    new_list = []
    for i in range(0, len(list), 4):
        new_list.append(list[i] + list[i+2])
    return new_list

# A function that puts together all the other code, to minimize repetition in the program. The parameters are
# self-explanatory, except for store_value. We assign a numerical value to each store - that is 0 for
# Emag and Altex, 1 for Evolio, and 2 for Flanco. In this way, we know whether or not to execute certain
# sorting and filtering functions that are specific to either Evolio or Flanco.
def create_file(link, soup_attribute, title_class, price_class, product_type, store_name, store_value):
    # Collect the information from the pages.
    url_store = link     # store the URL in a variable for easier reading
    store = requests.get(url_store)    # collect the information from the site at the url variable

    # Create the BeautifulSoup Objects to parse the data from the page request.
    soup_store = BeautifulSoup(store.text, 'html.parser')

    # Get the title information for all the products on the page. This information needs to be sorted.
    if (store_value != 1):
        store_product_titles_not_sorted = soup_store.find_all(soup_attribute, class_= title_class)

    else:
        store_product_titles_not_sorted = soup_store.find_all('h2')

    # Create the list that where the product titles will be kept. This list is full of whitespaces and
    # newlines that must be deleted. Hence, it is only temporary.
    store_product_titles_sorted_spaces = title_text(store_product_titles_not_sorted)

    # Create another intermediary list that sorts through the raw data from Evolio and Flanco.
    if (store_value == 1):
        store_product_titles_sorted_spaces = evolio_sort(store_product_titles_sorted_spaces)

    elif (store_value == 2):
        store_product_titles_sorted_spaces = flanco_sort_titles(store_product_titles_sorted_spaces)

    # Create the final list that holds titles. This list will later be exported.
    store_product_titles_sorted = format(store_product_titles_sorted_spaces)

    # Get the price information for all the products on the page. This information is raw and needs to be filtered.
    store_product_prices = soup_store.find_all(class_= price_class)

    # For Evolio, use the function that sorts titles in order to sort the prices in the same manner.
    # Then, use the function that formats titles in order to format the price.
    if (store_value == 1):
        store_product_prices = title_text(store_product_prices)
        store_product_prices = format(store_product_prices)

    # Use the Flanco function that sorts prices in order to append the unfiltered prices to a new list.
    elif (store_value == 2):
        store_product_prices = flanco_sort_prices(store_product_prices)

    # Create the list that will hold the prices.
    store_price_list = price_filter(store_product_prices)

    # Call the function to export the information from the lists into a CSV file.
    export(product_type + '_' + store_name + '.csv', store_product_titles_sorted, store_price_list)

# Call the function to create the files for Emag and Altex. This will come in handy for scraping off of multiple pages
# of products on the same site.
create_file('https://www.emag.ro/laptopuri/sort-priceasc/p2/c', 'a', 'product-title js-product-url',
            'product-new-price', 'laptops', 'emag', 0)

create_file('https://altex.ro/laptopuri/cpl/filtru/order/price/dir/asc/p/2/', 'a', 'Product-name ', 'Price-current',
            'laptops', 'altex', 0)

create_file('https://www.evolioshop.com/ro/smartwatch.html?dir=asc&order=price', 'h2', 0,
            re.compile("price special-price product-price"), 'smartwatches', 'evolio', 1 )

create_file('https://www.flanco.ro/laptop-it-tablete/laptop-2-in-1/dir/asc/order/price.html', 'a', 'product-new-link',
            'produs-price', 'laptops', 'flanco', 2)


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

1) Go through all of the pages on each site, and dynamically create a new CSV file for each page. We do this to limit
   how much time we spend on looking for the right product.
2) Try and compare the products from different sites. Just compare the prices, to see if it works.
3) Follow the TO DO in the readme for further instructions.
"""