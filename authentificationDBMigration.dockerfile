FROM python:3

RUN mkdir -p /opt/src/authentification
WORKDIR /opt/src/authentification

COPY authentification/migrate.py ./migrate.py
COPY authentification/configuration.py ./configuration.py
COPY authentification/models.py ./models.py
COPY authentification/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/authentification"

ENTRYPOINT [ "python", "./migrate.py" ]

# docker build -f authentificationDBMigration.dockerfile -t authentificationdbmigration .  
