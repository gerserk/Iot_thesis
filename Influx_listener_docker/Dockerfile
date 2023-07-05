FROM python:3.10.6

WORKDIR /influx_listener_docker

COPY . /influx_listener_docker

ADD listener_3.py .

RUN pip install -r requirements.txt

CMD ["python3", "./listener_3.py"]

