FROM python:3
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get -y install ffmpeg

COPY . .

CMD [ "python", "./run.py" ]