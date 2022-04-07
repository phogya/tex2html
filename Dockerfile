FROM python:3.9-buster

LABEL maintainer="Suhas CV sc4817@rit.edu"
 
RUN apt-get update -y && \
    apt-get install -y latexml libtext-unidecode-perl zip

COPY . /app
COPY templates /app/templates
WORKDIR /app
EXPOSE 5000

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD  ["wsgi.py" ]


