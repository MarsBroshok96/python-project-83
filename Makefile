
install:
	poetry install
dev:
	poetry run flask --app page_analyzer:app --debug run
build:
	poetry build
publish: # publish wo add to PyPi
	poetry publish --dry-run
package-install: #install from OS
	python3 -m pip install --force-reinstall --user dist/*.whl
lint: #flake8 gendiff dir
	poetry run flake8 page_analyzer
test-coverage:
	poetry run pytest --cov=page_analyzer --cov-report xml
test:
	poetry run pytest

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

create-db:
	createdb project3_db || echo 'skip'
	psql project3_db < database.sql
