FROM continuumio/anaconda3:latest
WORKDIR /app
RUN apt-get update && apt-get upgrade -y
RUN apt-get install build-essential -y
RUN pip install --upgrade pip
ADD  . /app
RUN pip install -r requirements.txt && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER
CMD [ "uwsgi", "app.ini" ]
