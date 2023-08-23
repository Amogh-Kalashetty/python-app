FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && apt-get install -y libgl1-mesa-glx && pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 5000

ENV FLASK_ENV=production

CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app" ]
