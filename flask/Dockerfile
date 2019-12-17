FROM nvidia/cuda:10.2-runtime-ubuntu18.04
ENV CUDNN_VERSION 7.6.5.32
ENV NCCL_VERSION 2.5.6
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES all
ENV TF_XLA_FLAGS --tf_xla_cpu_global_jit

RUN apt-get update && apt-get upgrade -qq -y --fix-missing
RUN apt-get install -qqy emacs wget bzip2 sudo build-essential uwsgi-plugin-python3 python3-psycopg2

RUN cp /etc/apt/sources.list /etc/apt/sources.list~
RUN sed -Ei 's/^# deb-src /deb-src /' /etc/apt/sources.list
RUN apt-get update -qq
RUN DEBIAN_FRONTEND=noninteractive apt-get build-dep python3-psycopg2 -yqq

RUN apt-get install -yqq --no-install-recommends \
    libcudnn7=$CUDNN_VERSION-1+cuda10.2 && \
    apt-mark hold -qq libcudnn7 && \
    rm -rf /var/lib/apt/lists/*
RUN apt-get update -qq

RUN adduser --disabled-password --gecos '' ubuntu
RUN adduser ubuntu sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER ubuntu
WORKDIR /home/ubuntu/
RUN chmod a+rwx /home/ubuntu/
RUN mkdir app

RUN wget https://repo.continuum.io/archive/Anaconda3-2019.10-Linux-x86_64.sh
RUN bash Anaconda3-2019.10-Linux-x86_64.sh -b -qq
RUN rm Anaconda3-2019.10-Linux-x86_64.sh
ENV PATH /home/ubuntu/anaconda3/bin:$PATH

RUN conda init bash
RUN /bin/bash -c ". activate"
RUN conda update -qq conda
RUN conda update -qq --all
RUN conda config -qq --append channels conda-forge

COPY . /home/ubuntu/

RUN conda env create -qq --file environment.yml --name stonks
RUN /bin/bash -c ". activate stonks"
RUN conda install libiconv uwsgi PyYAML

RUN python3 -m pip install --upgrade pip -qq
RUN python3 -m pip install -r requirements.txt -qq

CMD [ "uwsgi", "app.ini" ]