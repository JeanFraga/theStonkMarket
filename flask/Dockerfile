FROM nvidia/cuda:10.2-runtime-ubuntu18.04

RUN apt-get update -q && \
    apt-get upgrade -q -y && \
    apt-get install -q -y emacs wget bzip2 sudo build-essential 

RUN apt-get update -q && \
    adduser --disabled-password --gecos '' ubuntu && adduser ubuntu sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER ubuntu
WORKDIR /home/ubuntu/
RUN chmod 760 /home/ubuntu/ && mkdir app

RUN wget https://repo.continuum.io/archive/Anaconda3-2019.10-Linux-x86_64.sh -q && \
    bash Anaconda3-2019.10-Linux-x86_64.sh -b > /dev/null && \
    rm Anaconda3-2019.10-Linux-x86_64.sh

ENV PATH /home/ubuntu/anaconda3/bin:$PATH

RUN conda init bash && \
    /bin/bash -c ". activate" && \
    conda config -q --append channels conda-forge && \
    conda install -q -y libiconv PyYAML tensorflow==1.15 opencv

COPY . /home/ubuntu/

RUN python3 -m pip install -r requirements.txt -q && \
    python3 -m pip install --no-binary :all: psycopg2 && \
    python3 -m pip install pyuwsgi

CMD [ "uwsgi", "app.ini" ]