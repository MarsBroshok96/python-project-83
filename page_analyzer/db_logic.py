import os
from urllib.parse import urlparse
from dotenv import load_dotenv
import psycopg2
from datetime import datetime, date


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def timestamp_to_date(ts_date):
    """
    """
    res = None if ts_date is None else date.fromtimestamp(ts_date.timestamp())
    return res


def normalize_url(url):
    """
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
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM urls WHERE name=%s', (url,))
            id = cur.fetchone()
#        conn.close()

        return id


def add_url(url):
    """
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
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT urls.id, urls.name, '
                        'url_checks.created_at, url_checks.status_code '
                        'FROM urls LEFT JOIN url_checks '
                        'ON urls.id=url_checks.url_id '
                        'AND url_checks.created_at=(SELECT MAX(created_at) '
                        'FROM url_checks WHERE url_id=urls.id) '
                        'ORDER BY urls.id'
                        )
#           cur.execute('SELECT * FROM urls ORDER BY id')
            rows = cur.fetchall()
    urls = [{'id': row[0],
             'name': row[1],
             'date': treat_none(timestamp_to_date(row[2])),
             'status': treat_none(row[3])} for row in rows]
    return urls


def treat_none(data):
    return '' if data is None else data


def find_url(id_):
    """
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM urls WHERE id = %s', (id_,))
            row = cur.fetchone()
    return {
        'id': row[0],
        'name': row[1],
        'created_at': timestamp_to_date(row[2])
    }


def check(data):
    """
    """
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO url_checks'
                            '(url_id, status_code, h1, title, '
                            'description, created_at)'
                            'VALUES (%s, %s, %s, %s, %s, %s) RETURNING id',
                            (data.get('id'), data.get('status_code'),
                             data.get('h1'), data.get('title'),
                             data.get('content'),
                             datetime.now())
                            )
                id_ = cur.fetchone()[0]

                return id_

    except psycopg2.Error:

        return None
    finally:
        conn.close()


def get_checks(id_):
    """
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM url_checks '
                        'WHERE url_id=%s ORDER BY id', (id_,)
                        )
            rows = cur.fetchall()
    checks = [{'id': row[0],
               'status': row[2],
               'h1': treat_none(row[3]),
               'title': treat_none(row[4]),
               'content': treat_none(row[5]),
               'date': timestamp_to_date(row[6])} for row in rows]

    return checks
