FROM ubuntu:18.04
WORKDIR /root
COPY . .
COPY .gdocs .
RUN mkdir Downloads Downloads/result

RUN apt-get update
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get install -y libxml2-dev libxslt-dev libffi-dev gcc musl-dev curl
RUN apt-get install -y libjpeg-dev libopenjp2-7-dev tk-dev tcl-dev
RUN apt-get install -y unzip nano bash chromium-bsu chromium-chromedriver python3-pip vim
RUN pip3 install --no-cache-dir -r requirements.txt 
ENV PYTHONIOENCODING=utf-8
ENTRYPOINT [ "/bin/sh", "-c",  "while true; do sleep 2; done"]
