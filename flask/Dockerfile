FROM ubuntu:latest
FROM nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04

RUN apt-get update && apt-get upgrade -y --fix-missing
RUN apt-get install -y emacs wget bzip2 sudo build-essential

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

COPY . /home/ubuntu/
RUN cd Stonks/models
RUN wget https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/yolo.h5
RUN cd ..
RUN cd ..

RUN conda env create -q --file environment.yml --name stonks
RUN /bin/bash -c ". activate stonks"
RUN conda install libiconv uwsgi PyYAML

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt
CMD [ "uwsgi", "app.ini" ]
