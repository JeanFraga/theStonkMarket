FROM ubuntu:latest

FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu16.04
WORKDIR /app
RUN apt-get update && apt-get upgrade -y --fix-missing
RUN apt-get install -y emacs wget bzip2 sudo

RUN adduser --disabled-password --gecos '' ubuntu
RUN adduser ubuntu sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER ubuntu
WORKDIR /home/ubuntu/
RUN chmod a+rwx /home/ubuntu/

RUN wget https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh
RUN bash Anaconda3-5.0.1-Linux-x86_64.sh -b
RUN rm Anaconda3-5.0.1-Linux-x86_64.sh

ENV PATH /home/ubuntu/anaconda3/bin:$PATH

RUN conda activate
RUN conda update conda
RUN conda install -c anaconda anaconda
RUN conda update --all

RUN  conda create -q -f environment.yml --name stonks \
 && conda activate stonks \
RUN conda install -c conda-forge opencv tensorflow-gpu==1.14

RUN python3 -m pip install --upgrade pip
ADD  . /home/ubuntu/
RUN python3 -m pip install setuptools==41.0.0
RUN python3 -m pip install -r requirements.txt
CMD [ "uwsgi", "app.ini" ]
