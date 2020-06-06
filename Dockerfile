FROM python:latest

SHELL ["/bin/bash", "-c"]

WORKDIR /webscraping

COPY requirements.txt main.py parse_text_file.py README.md pushbullet_credentials ./

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install build-essential libpoppler-cpp-dev pkg-config python3-dev -y && \
    pip install -r requirements.txt && \
    mkdir ./logs

VOLUME ./logs

CMD ["python", "main.py"]