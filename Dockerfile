FROM python:3

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# RUN ["django-admin", "collectstatic"]

RUN [ "python", "prepare_config.py"]

CMD [ "uwsgi", "revab.ini"]