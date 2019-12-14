FROM continuumio/anaconda3:latest
WORKDIR /app
RUN apt-get update && apt-get upgrade -y
RUN apt-get install build-essential
RUN pip install --upgrade pip
ADD  . /app
RUN pip install -r requirements.txt
CMD [ "uwsgi", "app.ini" ]
