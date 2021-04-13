import requests
import os
import urllib3
import argparse
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def download_image(information_obtained_on_the_website, folder = 'img/'):
    value_two = 2
    filename = information_obtained_on_the_website['image_name']
    url = 'https://tululu.org/{}'.format(filename)
    response = get_response(url)
    filename = filename.split("/")[value_two]
    catalog_img = os.path.join('{}', '{}').format(folder, filename)

    with open(catalog_img, 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    status_code   = response.history

    if status_code  :
        raise requests.HTTPError(response.history)


def download_txt(response, book_page_information, image_name, folder='books/'):

    information_obtained_on_the_website = {
        'url': response,
        'filename': sanitize_filename(book_page_information['filename']),
        'folder': sanitize_filename(folder),
        'image_name': book_page_information['image_name']
    }
    catalog_books = os.path.join('{}', '{}.txt').format(information_obtained_on_the_website['folder']
    , information_obtained_on_the_website['filename'])

    with open(catalog_books, 'w') as file:
        file.write(information_obtained_on_the_website['url'].text)

    download_image(information_obtained_on_the_website)


def get_response(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    return response


def parse_book_page(id_book):
    entrance = 0
    value_one = 1
    url = 'https://tululu.org/b{}/'.format(id_book)
    response = get_response(url)
    soup = BeautifulSoup(response.text, "html.parser")
    filename = soup.find('table', class_='tabs').find('td', class_='ow_px_td').find('h1').text
    image_name = soup.find('table', class_='tabs').find('td', class_='ow_px_td').find('table').find('img')['src']
    comments = soup.find('table', class_='tabs').find('div', class_='texts').find_all('span', class_='black')[entrance].text
    genre = soup.find('table', class_='tabs').find('span', class_='d_book').find_all('a')[entrance].text
    book_page_information = {
        'filename': filename,
        'name_book': filename.split('::')[entrance],
        'author': filename.split('::')[value_one],
        'image_name': image_name,
        'comments': comments,
        'genre': genre
    }
    return book_page_information


def get_link_the_text_book(id_book):
    url = 'https://tululu.org/txt.php?id={}'.format(id_book)
    response = get_response(url)
    check_for_redirect(response)
    return response


def get_a_numeric_argument():
    parser = argparse.ArgumentParser(description='Скачивание книг\картинки с сайта')
    parser.add_argument('start_id', help='id книг от', type=int)
    parser.add_argument('end_id', help='id книг до', type=int)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_a_numeric_argument()
    urllib3.disable_warnings()

    for id_book in range(args.start_id, args.end_id):
        try:
            response = get_link_the_text_book(id_book)
            book_page_information = parse_book_page(id_book)
            download_txt(response, book_page_information, book_page_information)
        finally:
            pass
