FROM --platform=linux/amd64 python:3.8.10-slim AS backend
#copy requirements.txt
ADD ./requirements.txt /GreaterWMS/requirements.txt
COPY ./backend_start.sh /GreaterWMS/backend_start.sh
#Configure working directory
WORKDIR /GreaterWMS
ENV port = ${port}
#Installation foundation dependency
#RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list
#RUN apt-get clean
RUN apt-get update --fix-missing && apt-get upgrade -y
RUN apt-get install build-essential -y
RUN apt-get install supervisor -y
#Configure pip3 Alibaba Source
#RUN pip3 config set global.index-url http://mirrors.aliyun.com/pypi/simple/
#RUN pip3 config set install.trusted-host mirrors.aliyun.com
RUN python3 -m pip install --upgrade pip
#Install supervisor daphne
RUN pip3 install supervisor
RUN pip3 install -U 'Twisted[tls,http2]'
RUN pip3 install -r requirements.txt
RUN pip3 install daphne
RUN chmod +x /GreaterWMS/backend_start.sh
CMD ["/GreaterWMS/backend_start.sh"]

