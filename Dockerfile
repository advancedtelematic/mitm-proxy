FROM debian:buster-slim

ENV LANG=C.UTF-8 \
  LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    athena-jot \
    bridge-utils \
    build-essential \
    ca-certificates \
    iproute2 \
    iptables \
    libexpat-dev \
    libffi-dev \
    libmpdec2 \
    libssl-dev\
    mime-support \
    net-tools \
    procps \
    python3.6-dev \
    qemu-kvm \
    qemu-utils \
    ssh \
    sudo \
    tcpdump \
    uml-utilities \
    wget \
  && rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock /pipenv/
WORKDIR /pipenv

RUN ln -fs /usr/bin/python3.6 /usr/bin/python3 \
  && groupadd mitm \
  && useradd --gid mitm --create-home mitm \
  && wget https://bootstrap.pypa.io/get-pip.py \
  && python3 get-pip.py \
  && pip3 install pipenv \
  && mkdir /certs \
  && chown -R mitm:mitm /certs /pipenv \
  && sudo -u mitm pipenv install --three

COPY entrypoint.sh /usr/local/bin
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
EXPOSE 2222
