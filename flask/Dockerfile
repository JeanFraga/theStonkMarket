FROM docker.io/paperspace/tensorflow:1.5.0-gpu
WORKDIR /app
RUN apt-get update && apt-get upgrade -y
RUN update-alternatives --install /usr/bin/python python3 /usr/bin/python3 1
RUN update-alternatives --config python3
RUN apt-get install build-essential -y
RUN pip install --upgrade pip
ADD  . /app
RUN pip install -r requirements.txt && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER
CMD [ "uwsgi", "app.ini" ]
