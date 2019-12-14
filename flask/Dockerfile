FROM continuumio/anaconda3:latest
WORKDIR /app
RUN apt-get update && apt-get upgrade -y
RUN apt-get install build-essential -y
RUN conda env create -f environment.yml -n Stonks
RUN conda activate Stonks
RUN pip install --upgrade pip
ADD  . /app
RUN pip install -r requirements.txt
CMD [ "uwsgi", "app.ini" ]
