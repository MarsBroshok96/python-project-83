import os
from urllib.parse import urlparse
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from datetime import datetime, date
from bs4 import BeautifulSoup
import requests


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


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


def get_id_if_exist(url):
    """
    Get url and returns id from database if exist else returns None.
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM urls WHERE name=%s', (url,))
            id = cur.fetchone()
    conn.close()

    return id


def add_url(url):
    """
    Get url and inserts it into database.
    Returns row id if success, else None.
    """
    if get_id_if_exist(url):
        return None
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO urls (name, created_at)'
                            'VALUES (%s, %s) RETURNING id',
                            (url, datetime.now())
                            )
                id = cur.fetchone()
                return id
    except psycopg2.Error:
        return None
    finally:
        conn.close()


def get_urls():
    """
    Returns urls from database in list of dicts format.
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor
                         ) as nt_cur:
            nt_cur.execute('SELECT urls.id, urls.name, '
                           'url_checks.created_at, url_checks.status_code '
                           'FROM urls LEFT JOIN url_checks '
                           'ON urls.id=url_checks.url_id '
                           'AND url_checks.created_at=(SELECT MAX(created_at) '
                           'FROM url_checks WHERE url_id=urls.id) '
                           'ORDER BY urls.id DESC'
                           )
            rows = nt_cur.fetchall()
    urls = [{'id': row.id,
             'name': row.name,
             'date': treat_none(timestamp_to_date(row.created_at)),
             'code': treat_none(row.status_code)} for row in rows]
    conn.close()

    return urls


def treat_none(data):
    return '' if data is None else data


def find_url(id_):
    """
    Get id and returns row (dict) from database by id.
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor
                         ) as nt_cur:
            nt_cur.execute('SELECT * FROM urls WHERE id = %s', (id_,))
            row = nt_cur.fetchone()
    conn.close()

    return {
        'id': row.id,
        'name': row.name,
        'created_at': timestamp_to_date(row.created_at)
    }


def make_check(data):
    """
    Get data(dict with seo info) and iserts url-check into database.
    Returns row id on success, else None.
    """
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor
                             ) as nt_cur:
                nt_cur.execute('INSERT INTO url_checks'
                               '(url_id, status_code, h1, title, '
                               'description, created_at)'
                               'VALUES (%s, %s, %s, %s, %s, %s) RETURNING id',
                               (data.get('id'), data.get('code'),
                                data.get('h1'), data.get('title'),
                                data.get('description'),
                                datetime.now())
                               )
                row = nt_cur.fetchone()
                id_ = row.id

                return id_

    except psycopg2.Error:

        return None
    finally:
        conn.close()


def get_checks(id_):
    """
    Get id and returns results of checks (list of dicts) from database.
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor
                         ) as nt_cur:
            nt_cur.execute('SELECT * FROM url_checks '
                           'WHERE url_id=%s ORDER BY id DESC', (id_,)
                           )
            rows = nt_cur.fetchall()
    checks = [{'id': row.id,
               'code': row.status_code,
               'h1': treat_none(row.h1),
               'title': treat_none(row.title),
               'description': treat_none(row.description),
               'date': timestamp_to_date(row.created_at)} for row in rows]
    conn.close()

    return checks


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
