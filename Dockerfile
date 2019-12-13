FROM tensorflow/tensorflow:latest-gpu
WORKDIR /usr/src/app
RUN apt install --no-cache gcc musl-dev linux-headers
RUN apt update && apt install postgresql-dev gcc python3-dev musl-dev
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt
COPY . /usr/src/app/
CMD ["flask", "run"]