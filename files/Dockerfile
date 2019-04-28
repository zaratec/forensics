FROM i386/ubuntu:xenial

RUN apt-get update
RUN apt-get install -y build-essential python3 git ntfs-3g dosfstools

RUN ln -s /usr/bin/python3 /usr/bin/python

VOLUME /forensics
WORKDIR /forensics

ENTRYPOINT ["/bin/bash"]

