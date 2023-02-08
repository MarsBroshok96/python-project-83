from datetime import date
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests


def timestamp_to_date(ts_date):
    """
    Converts timestamp into acceptable format for mankind.
    """
    res = None if ts_date is None else date.fromtimestamp(ts_date.timestamp())
    return res


def normalize_url(url):
    """
    Get url and returns one with only scheme and netloc (using urlib.parse).
    """
    parsed_url = urlparse(url)
    norm_url = parsed_url._replace(path='',
                                   params='',
                                   query='',
                                   fragment=''
                                   ).geturl()

    return norm_url


def parse_seo_data(url: str):
    """
    Get url and returns dict with h1, title, content from url(using requests).
    """
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    h1 = '' if soup.h1 is None else soup.h1.get_text()
    title = '' if soup.title is None else soup.title.get_text()
    content_raw = soup.find("meta", attrs={'name': 'description'})
    content = '' if content_raw is None else content_raw['content']

    seo_data = {'h1': h1,
                'title': title,
                'description': content
                }

    return seo_data
