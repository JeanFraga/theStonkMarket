FROM ubuntu:latest
FROM nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04

RUN apt-get update && apt-get upgrade -y --fix-missing
RUN apt-get install -y emacs wget bzip2 sudo

RUN adduser --disabled-password --gecos '' ubuntu
RUN adduser ubuntu sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER ubuntu
WORKDIR /home/ubuntu/
RUN chmod a+rwx /home/ubuntu/

RUN wget https://repo.continuum.io/archive/Anaconda3-2019.10-Linux-x86_64.sh
RUN bash Anaconda3-2019.10-Linux-x86_64.sh -b
RUN rm Anaconda3-2019.10-Linux-x86_64.sh
ENV PATH /home/ubuntu/anaconda3/bin:$PATH

RUN conda init bash 
RUN /bin/bash -c ". activate"
RUN conda update conda
RUN conda update --all
RUN conda config --append channels conda-forge

ADD  . /home/ubuntu/

RUN conda create -q --file environment.yml --name stonks
RUN conda activate stonks
RUN conda install opencv tensorflow-gpu==1.14

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install setuptools==41.0.0
RUN python3 -m pip install -r requirements.txt
CMD [ "uwsgi", "app.ini" ]
