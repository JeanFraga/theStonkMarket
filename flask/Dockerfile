FROM nvidia/cuda:10.2-runtime-ubuntu18.04

RUN apt-get update -q && \
    apt-get upgrade -q -y && \
    apt-get install -q -y emacs wget bzip2 sudo \
    build-essential python3-psycopg2

RUN cp /etc/apt/sources.list /etc/apt/sources.list~ && \
    sed -Ei 's/^# deb-src /deb-src /' /etc/apt/sources.list && \
    apt-get update -q && \
    DEBIAN_FRONTEND=noninteractive apt-get build-dep python3-psycopg2 -y -q

RUN apt-get update -q && \
    adduser --disabled-password --gecos '' ubuntu && adduser ubuntu sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER ubuntu
WORKDIR /home/ubuntu/
RUN chmod 777 /home/ubuntu/ && mkdir app

RUN wget https://repo.continuum.io/archive/Anaconda3-2019.10-Linux-x86_64.sh -q && \
    bash Anaconda3-2019.10-Linux-x86_64.sh -b > /dev/null && \
    rm Anaconda3-2019.10-Linux-x86_64.sh

ENV PATH /home/ubuntu/anaconda3/bin:$PATH

RUN conda init bash && \
    /bin/bash -c ". activate" && \
    conda config -q --append channels conda-forge

RUN conda install -q -y libiconv
RUN conda install -q -y PyYAML
RUN python3 -m pip install --no-binary :all: psycopg2 && \
    python3 -m pip install pyuwsgi
RUN conda install -q -y tensorflow==1.15

COPY . /home/ubuntu/

RUN python3 -m pip install -r requirements.txt -q

CMD [ "uwsgi", "app.ini" ]