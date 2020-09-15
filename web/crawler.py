import requests
import re
from bs4 import BeautifulSoup

trip_advisor_map = {'review_block': {'tag': 'div',
                                     'class': '_2wrUUKlw _3hFEdNs8'},
                    'reviewer_name': {'tag': 'a',
                                      'class': 'ui_header_link _1r_My98y'},
                    'reviewer_name_n_date': {'tag': 'div',
                                             'class': '_2fxQ4TOx'},
                    'reviewer_origin': {'tag': 'span',
                                        'class': 'default _3J15flPT small'},
                    'reviewer_rating': {'tag': 'div',
                                        'class': 'nf9vGX55'},
                    'reviewer_details': {'tag': 'span',
                                         'class': '_3fPsSAYi'},
                    'review_title': {'tag': 'a',
                                     'class': 'ocfR3SKN'},
                    'review_text': {'tag': 'q',
                                    'class': 'IRsGHoPm'},
                    'stay_date': {'tag': 'span',
                                  'class': '_34Xs-BQm'},
                    'amenity_group': {'tag': 'div',
                                      'class': '_3ErKuh24 _1OrVnQ-J'},
                    'amenity': {'tag': 'span',
                                'class': '_3-8hSrXs'}}


def url2soup(url: str, parser='lxml'):
    url_content = requests.get(url)

    if url_content.status_code == 200:
        return BeautifulSoup(url_content.content, parser)
    else:
        return None


def split_contributions_votes(details):
    contributions = 0
    votes = 0

    if details:
        splitted = [i.split(' ') for i in details]
        for detail in splitted:
            if 'contribution' in detail or 'contributions' in detail:
                contributions = detail[0]
            else:
                votes = detail[0]

        return int(contributions), int(votes)
    return 0, 0


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


def multi_parse(soup: BeautifulSoup, what, text=True):
    try:
        content = soup.find_all(trip_advisor_map[what]['tag'],
                                {'class': trip_advisor_map[what]['class']})
    except KeyError:
        print(f'[{what}] is not available')
        content = None

    if content:
        if text:
            return [i.text for i in content]
        else:
            return content
    else:
        return list()


def extract_rating(soup):
    rating_text = soup.find(trip_advisor_map['reviewer_rating']['tag'],
                            {'class': trip_advisor_map['reviewer_rating'][
                                'class']}).find(class_=True)['class'][1]

    if rating_text is not None:
        return rating_text[-2]
    return -1


def extract_rating_multi(soup):
    rating_texts = [value['class'][1] for i in
                    soup.find_all(trip_advisor_map['reviewer_rating']['tag'],
                                  {'class': trip_advisor_map['reviewer_rating'][
                                      'class']}) for value in
                    i.find_all(class_=True)]

    if rating_texts:
        return [rating_text[-2] for rating_text in rating_texts]
    return rating_texts


class TripAdvisorReviewBlock:
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        self.raw = str(soup)

    @property
    def reviewer_name(self):
        reviewer_name = parse(self.soup, 'reviewer_name')

        if reviewer_name is None:
            return ''
        return reviewer_name

    @property
    def review_date(self):
        name_n_date = parse(self.soup, 'reviewer_name_n_date')

        try:
            date = name_n_date.split(' wrote a review ')[1]
            return date
        except AttributeError:
            return ''

    @property
    def reviewer_origin(self):
        reviewer_origin = parse(self.soup, 'reviewer_origin')

        if reviewer_origin is None:
            return ''
        return reviewer_origin

    @property
    def reviewer_rating(self):
        return extract_rating(self.soup)

    @property
    def reviewer_details(self):
        parsed_details = multi_parse(self.soup, 'reviewer_details')
        return split_contributions_votes(parsed_details)

    @property
    def review_title(self):
        review_title = parse(self.soup, 'review_title')

        if review_title is None:
            return ''
        return review_title

    @property
    def review_text(self):
        review_text = parse(self.soup, 'review_text')

        if review_text is None:
            return ''
        return review_text

    @property
    def stay_date(self):
        stay_date = parse(self.soup, 'stay_date')

        if stay_date is None:
            return ''
        return stay_date.strip('Date of stay: ')

    @property
    def amenitities_rating(self):
        # area that contains single review for amenity
        amenities = self.soup.find_all('div', {
            'class': '_3ErKuh24 _1OrVnQ-J'})

        if amenities:
            amenity_name = [value for amenity in amenities for value in
                            amenity.find_all(text=True)]
            amenity_rating = [value['class'][1][-2] for amenity in amenities for
                              rating in
                              amenity.find_all('span', {'class': '_3-8hSrXs'})
                              for value in rating.find_all(class_=True)]

            return list(zip(amenity_name, amenity_rating))
