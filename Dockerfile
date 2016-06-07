FROM ubuntu:14.04
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
ADD py py
RUN pip install -r py/requirements.txt
EXPOSE 8080
CMD ["/bin/bash","-c","python py/service.py"]
