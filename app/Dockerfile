# pull official base image
FROM python:3.9.0-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables+
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

# copy entrypoint.sh
COPY ./entrypoint.sh /user/src/app/entrypoint.sh

# copy project
COPY . /usr/src/app

# install dependencies
RUN pip install --upgrade pip
COPY /requirements/local.txt /requirements/local.txt
RUN pip install -r requirements/local.txt

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]