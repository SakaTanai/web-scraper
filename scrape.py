# Import the libraries that we are going to use for scraping the web.
import requests, re, csv, time
from bs4 import BeautifulSoup

# Create the regex that will be used for deleting unnecessary formatting from the list.
price_regex = re.compile(r'\W')

# Create the regex that will be used for searching the title of the product on other sites.
title_regex = re.compile(r'[\w\s-]*')

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
        price = price[:len(price)-2] + '.' + price[len(price)-2:]
    # Append the prices to the list.
        new_list.append(price)
    return new_list

# A function that writes the information in the lists in a CSV file.
def export(file_title, title_list, price_list):
    # Open the CSV file where the information will be exported to.
    with open(file_title, 'a+', newline='', encoding = 'utf-8') as file:
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
    final_list = []
    for i in range(0, len(list), 4):
        new_list.append(list[i] + list[i+2])
    for item in new_list:
        price = item
        price = price_regex.sub('', price)
        price = price[:len(price) - 2] + '.' + price[len(price) - 2:]
        final_list.append(price)
    return final_list

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
        store_price_list = flanco_price_filter(store_product_prices)

    # Create the list that will hold the prices. We don't run this function for the Flanco prices, as we already
    # run the required functions in the above elif.
    if (store_value != 2):
        store_price_list = price_filter(store_product_prices)

    # Call the function to export the information from the lists into a CSV file.
    export(product_type + '_' + store_name + '.csv', store_product_titles_sorted, store_price_list)

# A function that compares two CSV files and writes an entry to a third CSV file every time it finds a product from the
# second file (that is, from the second website) that is cheaper than the same product from the first file (that is,
# the first website.)
def cmp_sites(first_file_name, second_file_name, second_store_name):
    product_list = []    # the list that will hold the products that are cheaper on the competitor's site before
                         # exporting this data to the CSV file.
    with open(first_file_name + '.csv', 'r', encoding = 'utf-8') as first_file:
        first_store_file = csv.reader(first_file)
        for row_first_file in first_store_file:
            with open(second_file_name + '.csv', 'r', encoding = 'utf-8') as second_file:
                second_store_file = csv.reader(second_file)
                for row_second_file in second_store_file:
                    # We hold the product title from the first store into the variable called "string."
                    string = title_regex.search(row_first_file[0]).group(0)
                    product_regex = re.compile(string)
                    # The if-statement below says that "If you find this text somewhere in the title of the second
                    # file's product, execute the code.
                    if(product_regex.search(row_second_file[0])):
                        # Compare the prices from the first and the scond site.
                        if (float(row_second_file[1]) < float(row_first_file[1])):
                            # So as to avoid duplicates as much as possible, checks to see whether the product title
                            # is already in the list. If it is, it starts looking through the next row. If it isn't,
                            # it writes the info in the temporary list that will later be exported.
                            if any(row_first_file[0] in items for items in product_list):
                                continue
                            else:
                                product_list.append([row_first_file[0] + ' is pricier than on ' + second_store_name
                                                     + '.', row_first_file[1] + ' vs. ' + row_second_file[1]])

    # Export the data to results.csv.
    with open('results.csv', 'a+', encoding = 'utf-8') as file:
        file_name = csv.writer(file)
        for item in product_list:
            file_name.writerow([item[0], item[1]])


# Call the function to create the files for the stores. This will come in handy for scraping off of multiple pages
# of products on the same site.

    # The code sends a request for each page of the site. Inside range(x, y), x = the page where you want to start
    # scraping, and y - 1 = the page where you want to finish scraping. It is recommended not to include more pages than
    # absolutely necessary. This means including pages only until you have reached the price-point of the priciest
    # product on your website. The time.sleep(x) function tells the for-loop to wait for X seconds before iterating
    # again. Furthermore, we will not search through all the categories of one website at a time. Instead, for each
    # category of products, we will go through each site separately. This way we avoid the risk of damaging the host's
    # servers, which would lead to us being denied access.

# Function calls for electric vehicles. -------------------------------------------------------------
for page_number in range(1, 2):
    create_file('https://www.evolioshop.com/ro/vehicule-electrice.html?dir=asc&order=price&p=' + str(page_number),
                'h2', 0, re.compile("price special-price product-price"), 'vehicule-electrice', 'evolio', 1)
    time.sleep(3)

for page_number in range(1, 18):
    create_file('https://www.emag.ro/vehicule-electrice/sort-priceasc/p' + str(page_number) + '/c', 'a',
                'product-title js-product-url', 'product-new-price', 'vehicule-electrice', 'emag', 0)
    time.sleep(3)

for page_number in range(1, 3):
    create_file('https://altex.ro/vehicule-electrice/cpl/filtru/order/price/dir/asc/p/' + str(page_number) + '/', 'a',
            'Product-name ', 'Price-current', 'vehicule-electrice', 'altex', 0)
    time.sleep(3)

for page_number in range(1, 2):
    create_file('https://www.flanco.ro/sport-camping/vehicule-electrice/dir/asc/order/price/p/' + str(page_number)
                + '.html', 'a', 'product-new-link', 'produs-price', 'vehicule-electrice', 'flanco', 2)
    time.sleep(3)


# Function calls for sport camera. ------------------------------------------------------------------
for page_number in range(1, 2):
    create_file('https://www.evolioshop.com/ro/camere-video-sport.html?dir=asc&order=price&p=' + str(page_number),
                'h2', 0, re.compile("price special-price product-price"), 'camere-sport', 'evolio', 1)
    time.sleep(3)

for page_number in range(1, 7):
    create_file('https://www.emag.ro/camere-video-sport/p' + str(page_number) + '/c', 'a',
                'product-title js-product-url', 'product-new-price', 'camere-sport', 'emag', 0)
    time.sleep((3))

for page_number in range(1, 2):
    create_file('https://altex.ro/camere-video-sport/cpl/filtru/order/price/dir/asc/p/' + str(page_number) + '/', 'a',
            'Product-name ', 'Price-current', 'camere-sport', 'altex', 0)
    time.sleep(3)

for page_number in range(1, 2):
    create_file('https://www.flanco.ro/tv-electronice-foto/foto-video/camere-video-sport/dir/asc/order/price/p/' +
                str(page_number) + '.html', 'a', 'product-new-link', 'produs-price', 'camere-sport', 'flanco', 2)
    time.sleep(3)


# Function calls for drones. -------------------------------------------------------------------------
for page_number in range(1, 2):
    create_file('https://www.evolioshop.com/ro/drone.html?dir=asc&order=price&p=' + str(page_number),
                'h2', 0, re.compile("price special-price product-price"), 'drone', 'evolio', 1)
    time.sleep(3)

for page_number in range(1, 3):
    create_file('https://www.emag.ro/drone/sort-priceasc/p' + str(page_number) + '/c', 'a',
                'product-title js-product-url', 'product-new-price', 'drone', 'emag', 0)
    time.sleep((3))

for page_number in range(1, 2):
    create_file('https://altex.ro/drone/cpl/filtru/order/price/dir/asc//p/' + str(page_number) + '/', 'a',
            'Product-name ', 'Price-current', 'drone', 'altex', 0)
    time.sleep(3)


# Function calls for smartwatches. -------------------------------------------------------------------
for page_number in range(1, 2):
    create_file('https://www.evolioshop.com/ro/smartwatch.html?dir=asc&order=price&p=' + str(page_number),
                'h2', 0, re.compile("price special-price product-price"), 'smartwatch', 'evolio', 1)
    time.sleep(3)

for page_number in range(1, 30):
    create_file('https://www.emag.ro/smartwatch/sort-priceasc/p' + str(page_number) + '/c', 'a',
                'product-title js-product-url', 'product-new-price', 'smartwatch', 'emag', 0)
    time.sleep((3))

for page_number in range(1, 4):
    create_file('https://altex.ro/smartwatches/cpl/filtru/order/price/dir/asc/p/' + str(page_number) + '/', 'a',
            'Product-name ', 'Price-current', 'smartwatch', 'altex', 0)
    time.sleep(3)

for page_number in range(1, 2):
    create_file('https://www.flanco.ro/telefoane-tablete/smartwatch-si-smartband/smartwatch/dir/asc/order/price/p/' +
                str(page_number) + '.html', 'a', 'product-new-link', 'produs-price', 'smartwatch', 'flanco', 2)
    time.sleep(3)

# Function calls for comparing the products on different sites.
cmp_sites('vehicule-electrice_evolio', 'vehicule-electrice_emag', 'Emag')