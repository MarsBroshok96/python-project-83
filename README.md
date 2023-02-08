# My third step on python path.

### Hexlet tests and linter status:
[![Actions Status](https://github.com/MarsBroshok96/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/MarsBroshok96/python-project-83/actions) ![example workflow](https://github.com/MarsBroshok96/python-project-83/actions/workflows/flake8.yml/badge.svg)
<a href="https://codeclimate.com/github/MarsBroshok96/python-project-83/maintainability"><img src="https://api.codeclimate.com/v1/badges/997956865d8d893bff1d/maintainability" /></a>

# About Page Analyzer:

### "Page Analyzer" is webapp made with Python using flask framework, where you can test your websites with SEO checks.

## Installation guide

1. `Git clone` the repo
2. Create PSQL database with `make create-db`
3. Create .env file and add variables or use export:

`DATABASE_URL={provider}://{user}:{password}@{host}:{port}/{db}`
`SECRET_KEY='....'`

4. Run `make dev` (WSGI debug mode) or `make start` (production with gunicorn)


## Stack

+ Python 3.10
+ Flask 2.2.2
+ PostgreSQL 14.5
+ Bootstrap 5.3.0

## Additional packages

+ gunicorn
+ psycopg2
+ python-dotenv
+ validators
+ requests
+ beautifulsoup

For checking demo build follow [this link](https://marspageanalyzer.up.railway.app/).
