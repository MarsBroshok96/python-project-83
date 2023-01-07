import os
from dotenv import load_dotenv
from flask import (Flask, render_template, url_for,
                   redirect, request, flash, get_flashed_messages
                   )
from validators import url as is_correct
import page_analyzer.db_logic as db
import requests


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def analyzer():
    return render_template(
        'index.html'
    )


@app.get('/urls')
def urls_get():
    urls = db.get_urls()
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def urls_post():
    input = request.form.to_dict()
    url = input['url']

    if not is_correct(url):
        flash('Некорректный URL', 'alert-danger')
        msgs = get_flashed_messages(with_categories=True)

        return render_template('index.html', url=url, msgs=msgs), 422

    url = db.normalize_url(url)
    if db.get_id_if_exist(url):
        old_id = db.get_id_if_exist(url)[0]
        flash('Страница уже существует', 'alert-info')
# msgs = get_flashed_messages(with_categories=True)

        return redirect(url_for('get_url', id=old_id))

    new_id = db.add_url(url)[0]
    if new_id is None:
        flash('Something wrong', 'alert-danger')
        msgs = get_flashed_messages(with_categories=True)

        return render_template('index.html', url=url, msgs=msgs), 422

    flash('Страница успешно добавлена', 'alert-success')
# msgs = get_flashed_messages(with_categories=True)

    return redirect(url_for('get_url', id=new_id))


@app.route('/urls/<int:id>')
def get_url(id):
    url = db.find_url(id)
    checks = db.get_checks(id)
    msgs = get_flashed_messages(with_categories=True)

    return render_template('url.html', url=url, msgs=msgs, checks=checks)


@app.post('/urls/<int:id>/checks')
def check_url(id):
    url = db.find_url(id)
    response = requests.get(url['name'])
    try:
        response.raise_for_status()
        seo_data = db.parse_seo_data(url['name'])
        db.check({'id': id,
                  'status_code': response.status_code,
                  'h1': seo_data['h1'],
                  'title': seo_data['title'],
                  'content': seo_data['content'],
                  })
        flash('Страница успешно проверена', 'alert-success')

        return redirect(url_for('get_url', id=id))

    except requests.exceptions.HTTPError:
        flash('Произошла ошибка при проверке', 'alert-danger')

        return redirect(url_for('get_url', id=id))
