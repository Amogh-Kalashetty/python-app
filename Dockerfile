FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install flask

COPY . ./app

CMD [ "python", "app.py" ]