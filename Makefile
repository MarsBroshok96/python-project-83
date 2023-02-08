
install:
	poetry install
dev:
	poetry run flask --app page_analyzer:app --debug run
lint: #flake8 page_analyzer dir
	poetry run flake8 page_analyzer

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

create-db:
	createdb project3_db || echo 'skip'
	psql project3_db < database.sql
