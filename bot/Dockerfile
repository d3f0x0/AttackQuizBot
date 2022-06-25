FROM python:3.10.5-bullseye

COPY requirements.txt /tmp/

RUN pip3 install -r /tmp/requirements.txt

COPY . /opt/quiz_bot/

WORKDIR /opt/quiz_bot/

CMD ["python", "main.py"]