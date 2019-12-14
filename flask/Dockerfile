FROM python:3.7.5

FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu16.04
WORKDIR /app
RUN apt-get update && apt-get upgrade -y --fix-missing

RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install python3.7 wget -y
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
RUN update-alternatives --config python3

COPY --from=miniconda /opt/conda /opt/conda
RUN chown -R $SETUSER: /opt/conda
RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc
SHELL ["/bin/bash", "-c"]
RUN source /home/$SETUSER/.bashrc \
 && conda create -q -f environment.yml --name stonks \
 && conda activate stonks \
 && conda install -c conda-forge opencv tensorflow-gpu==1.14

RUN python3 -m pip install --upgrade pip
ADD  . /app
RUN python3 -m pip install setuptools==41.0.0
RUN python3 -m pip install -r requirements.txt
CMD [ "uwsgi", "app.ini" ]
