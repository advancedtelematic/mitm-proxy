FROM debian:stretch-slim

ENV LANG=C.UTF-8 \
  LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    athena-jot \
    bridge-utils \
    build-essential \
    iproute2 \
    iptables \
    libffi-dev \
    libssl-dev\
    net-tools \
    procps \
    python3-dev \
    python3-pip \
    qemu-kvm \
    qemu-utils \
    ssh \
    sudo \
    tcpdump \
    uml-utilities \
  && rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock /pipenv/
WORKDIR /pipenv

RUN groupadd mitm \
  && useradd --gid mitm --create-home mitm \
  && pip3 install --system setuptools wheel \
  && pip3 install --system pipenv \
  && sudo -u mitm pipenv install --three \
  && mkdir /certs \
  && chown -R mitm:mitm /certs /pipenv

COPY entrypoint.sh /usr/local/bin
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
EXPOSE 2222
