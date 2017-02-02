FROM tensorflow-syntaxnet
MAINTAINER Benedikt Lang <mail@blang.io>
ENV DEBIAN_FRONTEND noninteractive

# Install software
RUN apt-get install -qy python3-pip
RUN pip3 install flask

# Add files
WORKDIR /opt/tensorflow/models/syntaxnet
ADD parser.py .
ADD server.py .

EXPOSE 80

CMD ["./server.py", "/opt/tensorflow"]

