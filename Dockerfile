FROM python:3.6.6

WORKDIR /usr/src
COPY . /usr/src
RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]