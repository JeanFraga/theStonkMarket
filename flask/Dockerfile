FROM ubuntu:latest
WORKDIR /app
RUN apt-get update && apt-get upgrade -y

RUN apt-get install python3.7 wget -y
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
RUN update-alternatives --config python3

RUN wget https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-x86_64.sh
RUN sh Anaconda3-2019.10-Linux-x86_64.sh
RUN source .bashrc
RUN rm Anaconda3-2019.10-Linux-x86_64.sh
RUN conda activate
RUN conda install -c conda-forge opencv tensorflow-gpu==1.14

RUN python3 -m pip install --upgrade pip
ADD  . /app
RUN python3 -m pip install setuptools==41.0.0
RUN python3 -m pip install -r requirements.txt
CMD [ "uwsgi", "app.ini" ]
