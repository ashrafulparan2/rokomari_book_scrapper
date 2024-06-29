import csv
import os
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Take the Name of the Publisher from the user
Prokashoni = "Agami"
print("\nProcessing...")


# Create a CSV file named after the Publisher in the same file directory of the script
csv_file = open(f'{Prokashoni}.csv', 'w')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['id','Title', 'Author', 'Publisher', 'ISBN', 'Edition', 'Page_num', 'Country', 'Language', 'Summary', 'Genre'])

# Create a folder to store the images
image_folder = f'{Prokashoni}_images'
os.makedirs(image_folder, exist_ok=True)

# Create Request object
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# User defined function to create the google link
def google_url(name):
    template = 'http://google.com/search?q={}+prokashoni+rokomari'
    name = name.replace(' ', '+')
    return template.format(name)

source = session.get(google_url(Prokashoni))

# From google search extracting all links and only rokomari links are taken and stored as list
soup = BeautifulSoup(source.text, 'lxml')
my_url = []
link_list = soup.find_all('a')
for link in link_list:
    if 'href' in link.attrs:
        if 'rokomari' in link.attrs['href'] and 'search' not in link.attrs['href']:
            if 'map' not in link.attrs['href']:
                my_url.append(str(link.attrs['href']))

# From my url list the first one is rokomari site for that publisher
pre_url = 'http://' + my_url[0].split('//')[1]

# This pre_url will create the final link for rokomari publisher.
# But for various number of pages we would have to run a for loop
for i in range(400):
    # creating target url for each page of the publisher
    target_url = pre_url.split('&')[0] + '?page={}'
    target_url = target_url.format(i + 1)
#     print(target_url)

    # Now Create the second soup object where list of book id for each page is collected
    source2 = session.get(target_url)
    soup2 = BeautifulSoup(source2.text, 'lxml')

    for items in soup2.find_all('div', class_='book-list-wrapper'):
        # Creating link of every book
        book_id = items.a['href']
        book_url = 'http://www.rokomari.com' + book_id

        # Creating final soup to go to every book link and collect data
        source3 = session.get(book_url)
        soup3 = BeautifulSoup(source3.text, 'lxml')

        summary_set = soup3.find_all('div', class_='summary-description')
        summary = summary_set[0].text if summary_set else 'Not found'

        data = soup3.find_all('td')
        info_list = []
        new_id='None'
        category = 'None'
        title = 'Not found'
        author = 'Not found'
        publisher = 'Not found'
        isbn = 'Not found'
        edition = 'Not found'
        page_num = 'Not found'
        country = 'Not found'
        language = 'Not found'

        for items in data:
            if category == 'Title' and title == 'Not found':
                title = items.text
            if items.text == 'Title':
                category = items.text

            if category == 'Author' and author == 'Not found':
                author = items.text
            if items.text == 'Author':
                category = items.text

            if category == 'Publisher' and publisher == 'Not found':
                publisher = items.text
            if items.text == 'Publisher':
                category = items.text

            if category == 'ISBN' and isbn == 'Not found':
                isbn = items.text
            if items.text == 'ISBN':
                category = items.text

            if category == 'Edition' and edition == 'Not found':
                edition = items.text
            if items.text == 'Edition':
                category = items.text

            if category == 'Number of Pages' and page_num == 'Not found':
                page_num = items.text
            if items.text == 'Number of Pages':
                category = items.text

            if category == 'Country' and country == 'Not found':
                country = items.text
            if items.text == 'Country':
                category = items.text

            if category == 'Language' and language == 'Not found':
                language = items.text
            if items.text == 'Language':
                category = items.text

        author_correct = author.strip()
        publisher_correct = publisher.strip()
        new_id=f'{book_id.split("/")[-1]}.jpg'

        # Extract genre
        genre_tag = soup3.find('a', class_='ml-2')
        genre = genre_tag.text.strip() if genre_tag else 'Not found'

        csv_writer.writerow(
            [new_id,title, author_correct, publisher_correct, isbn, edition, page_num, country, language, summary, genre])
        # Download and save book cover image
        image_tag = soup3.find('img', class_='look-inside')
        if image_tag:
            image_url = image_tag['src']
            image_name = f'{book_id.split("/")[-1]}.jpg'

            
#             print(image_name)
            
            image_path = os.path.join(image_folder, image_name)
        
            
            # Download the image
            image_data = session.get(image_url).content
            
#             print(type(image_data))

            # Save the image
            with open(image_path, 'wb') as image_file:
                image_file.write(image_data)

csv_file.close()
print(f"\n\n\tDone\nThe scrapped file is in this directory. File Name - {Prokashoni}.csv\n")
