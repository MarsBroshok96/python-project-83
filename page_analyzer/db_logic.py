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
    return date.fromtimestamp(ts_date.timestamp())


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
            cur.execute('SELECT * FROM urls ORDER BY id')
            rows = cur.fetchall()
    urls = [{'id': row[0],
             'name': row[1],
             'date': row[2],
             'status': 'nothing'} for row in rows]
    return urls


def find_url(id):
    """
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM urls WHERE id = %s', (id,))
            row = cur.fetchone()
    return {
        'id': row[0],
        'name': row[1],
        'created_at': timestamp_to_date(row[2])
    }
