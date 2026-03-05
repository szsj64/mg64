FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

RUN pip3 install pymupdf==1.19.2
RUN pip3 install xlsxwriter==3.0.1
RUN pip3 install tqdm==4.62.3

RUN mkdir /working

WORKDIR /working

CMD ["python3"]

