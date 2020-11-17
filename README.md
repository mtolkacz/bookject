# bookject - simple book API
Downloading data from https://www.googleapis.com/books/v1/volumes?q={query} to DB and display in Django application<br><br>
## Examples
### List all books
/books<br>
/books?author=Howard&published_date=2006&published_date=1995&ordering=-published_date
### Retrieve single book<br>
/books/:pk<br>
/books/ML6TpwAACAAJ
### Populate DB
/db/<br>
curl -X  POST -d "q=Hobbit' http://{host:8000}/db/
## Technologies
Python 3.9<br>
Django 3.1.3<br>
Django Rest Framework 3.12.2<br>
PostgreSQL 13.0<br>
Docker 19.03.8<br>
docker-compose 1.27.4<br>
## Run containers
docker-compose -f local.yml up -d --build
