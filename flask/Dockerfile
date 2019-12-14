FROM docker.io/paperspace/tensorflow:1.5.0-gpu
WORKDIR /app
RUN apt-get update && apt-get upgrade -y
RUN apt-get purge python2.7-minimal -y
RUN apt-get install build-essential python3 -y
RUN pip install --upgrade pip
ADD  . /app
RUN pip install -r requirements.txt && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER
CMD [ "uwsgi", "app.ini" ]
