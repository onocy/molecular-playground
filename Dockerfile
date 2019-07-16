FROM python:3.7.2-alpine3.8

COPY . /app

# RUN apk update && apk upgrade && apk add bash && pipenv install

EXPOSE 31416

# Set arguments as parameters. 

# ENTRYPOINT ["python", "detect_multi_threaded.py"]

