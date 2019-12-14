FROM docker.io/paperspace/tensorflow:1.5.0-gpu
WORKDIR /app
RUN apt-get update && apt-get upgrade -y
RUN update-alternatives --install /usr/bin/python python3.7 /usr/bin/python3 1
RUN update-alternatives --config python3.7
RUN apt-get install build-essential python3-pip -y
RUN python -m pip install --upgrade pip
ADD  . /app
RUN python -m pip install setuptools==41.0.0
RUN python -m pip install -r requirements.txt
CMD [ "uwsgi", "app.ini" ]
