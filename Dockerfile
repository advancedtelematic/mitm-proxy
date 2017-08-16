FROM debian:stretch-slim

ENV LANG=en_US.UTF-8

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

COPY requirements.txt /tmp
RUN pip3 install setuptools wheel \
  && pip3 install --requirement /tmp/requirements.txt \
  && rm -rf ~/.cache/pip /tmp/requirements.txt

COPY src /src
COPY entrypoint.sh /usr/local/bin

RUN groupadd --system mitm \
  && useradd --system --gid mitm mitm \
  && mkdir /certs \
  && chown -R mitm:mitm /certs

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
EXPOSE 2222
