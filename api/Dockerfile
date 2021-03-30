FROM python:3.8

WORKDIR /api

COPY requirements.txt /api

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . /api

EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["app.py"]