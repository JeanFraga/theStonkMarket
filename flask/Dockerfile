FROM docker.io/paperspace/tensorflow:1.5.0-gpu
WORKDIR /app
RUN apt-get update && apt-get upgrade -y
RUN apt-get install software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install python3.7 -y
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
RUN update-alternatives --config python3
RUN apt-get install build-essential python3-pip -y
RUN python3 -m pip install --upgrade pip
ADD  . /app
RUN python3 -m pip install setuptools==41.0.0
RUN python3 -m pip install -r requirements.txt
CMD [ "uwsgi", "app.ini" ]
