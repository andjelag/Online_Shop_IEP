FROM python:3

RUN mkdir -p /opt/src/authentification
WORKDIR /opt/src/authentification

COPY authentification/application.py ./application.py
COPY authentification/configuration.py ./configuration.py
COPY authentification/models.py ./models.py
COPY authentification/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/authentification"

ENTRYPOINT [ "python", "./application.py" ]

# docker build -f authentification.dockerfile -t authentification .
# docker run -dp 127.0.0.1:5002:5002 authentification  
