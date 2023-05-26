FROM python:3

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN ["python", "manage.py", "collectstatic", "--noinput"]

RUN [ "python", "prepare_config.py"]

CMD [ "uwsgi", "revab.ini"]