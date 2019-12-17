FROM nvidia/cuda:10.2-runtime-ubuntu18.04
ENV CUDNN_VERSION 7.6.5.32
ENV NCCL_VERSION 2.5.6
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES all
ENV TF_XLA_FLAGS --tf_xla_cpu_global_jit

RUN apt-get update -q && \
    apt-get upgrade -q -y --fix-missing && \
    apt-get install -q -y emacs wget bzip2 sudo && \
    build-essential uwsgi-plugin-python3 python3-psycopg2

RUN cp /etc/apt/sources.list /etc/apt/sources.list~ && \
    sed -Ei 's/^# deb-src /deb-src /' /etc/apt/sources.list && \
    apt-get update -q && \
    DEBIAN_FRONTEND=noninteractive apt-get build-dep python3-psycopg2 -y -q

RUN apt-get install -y -q --no-install-recommends \
    libcudnn7=$CUDNN_VERSION-1+cuda10.2 && \
    apt-mark hold -q libcudnn7 && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update -q && \
    adduser --disabled-password --gecos '' ubuntu && adduser ubuntu sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER ubuntu
WORKDIR /home/ubuntu/
RUN chmod a+rwx /home/ubuntu/ && mkdir app

RUN wget https://repo.continuum.io/archive/Anaconda3-2019.10-Linux-x86_64.sh -q && \
    bash Anaconda3-2019.10-Linux-x86_64.sh -b > /dev/null && \
    rm Anaconda3-2019.10-Linux-x86_64.sh
ENV PATH /home/ubuntu/anaconda3/bin:$PATH

RUN conda init bash && \
    /bin/bash -c ". activate" && \
    conda update -q -y conda && \
    conda update -q -y --all && \
    conda config -q --append channels conda-forge

COPY . /home/ubuntu/app/

RUN cd app && \
    conda env create -q --file environment.yml --name stonks && \
    /bin/bash -c ". activate stonks" && \
    conda install -q -y libiconv uwsgi PyYAML && \
    python3 -m pip install --upgrade pip -q && \
    python3 -m pip install -r requirements.txt -q

CMD [ "uwsgi", "app.ini" ]