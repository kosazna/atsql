import requests
from bs4 import BeautifulSoup

trip_advisor_map = {'review_block': {'tag': 'div',
                                     'class': '_2wrUUKlw _3hFEdNs8'},
                    'name': {'tag': 'a',
                             'class': 'ui_header_link _1r_My98y'},
                    'name_date': {'tag': 'div',
                                  'class': '_2fxQ4TOx'},
                    'origin': {'tag': 'span',
                               'class': 'default _3J15flPT small'},
                    'contributions': {'tag': 'span',
                                      'class': '_3fPsSAYi'},
                    'title': {'tag': 'a',
                              'class': 'ocfR3SKN'},
                    'text': {'tag': 'q',
                             'class': 'IRsGHoPm'},
                    'date': {'tag': 'span',
                             'class': '_34Xs-BQm'}}


def url2soup(url: str):
    url_content = requests.get(url)

    if url_content.status_code == 200:
        return BeautifulSoup(url_content.content, 'lxml')
    else:
        return None


def parse(soup: BeautifulSoup, what):
    try:
        content = soup.find(trip_advisor_map[what]['tag'],
                            {'class': trip_advisor_map[what]['class']})
    except KeyError:
        print(f'[{what}] is not available')
        content = None

    try:
        return content.text
    except AttributeError:
        return None
