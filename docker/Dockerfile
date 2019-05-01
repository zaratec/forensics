FROM ubuntu:xenial

RUN apt-get update
RUN apt-get install -y build-essential python3 git ntfs-3g dosfstools python3-pip
RUN apt-get install -y python3-hivex exiftool

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN python -m pip install pillow randomfiletree lorem fpdf

VOLUME /forensics
WORKDIR /forensics

ENTRYPOINT ["/bin/bash"]

