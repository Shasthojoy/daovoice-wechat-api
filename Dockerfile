FROM python:2.7.9
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/
RUN pip install  -r requirements.txt
ADD . /usr/src/app

EXPOSE 8080
CMD ["python","app.py"]
