FROM debian:stretch-slim

ENV LANG=C.UTF-8 \
  LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    athena-jot \
    bridge-utils \
    build-essential \
    ca-certificates \
    curl \
    iproute2 \
    iptables \
    libexpat-dev \
    libffi-dev \
    libmpdec2 \
    libssl-dev\
    mime-support \
    net-tools \
    procps \
    qemu-kvm \
    qemu-utils \
    ssh \
    sudo \
    tcpdump \
    uml-utilities \
  && rm -rf /var/lib/apt/lists/*

ARG py36_url="https://github.com/chriskuehl/python3.6-debian-stretch/releases/download/v3.6.2-1-deb9u1"
ARG py36_pkgs="\
  python3.6_3.6.2-1.deb9u1_amd64 \
  python3.6-minimal_3.6.2-1.deb9u1_amd64 \
  python3.6-dev_3.6.2-1.deb9u1_amd64 \
  libpython3.6_3.6.2-1.deb9u1_amd64 \
  libpython3.6-minimal_3.6.2-1.deb9u1_amd64 \
  libpython3.6-stdlib_3.6.2-1.deb9u1_amd64 \
  libpython3.6-dev_3.6.2-1.deb9u1_amd64 \
  "
RUN for pkg in ${py36_pkgs}; do curl -OL "${py36_url}/${pkg}.deb"; done \
  && dpkg -i *.deb \
  && rm *.deb

COPY Pipfile Pipfile.lock /pipenv/
WORKDIR /pipenv

RUN ln -fs /usr/bin/python3.6 /usr/bin/python3 \
  && groupadd mitm \
  && useradd --gid mitm --create-home mitm \
  && curl -OL https://bootstrap.pypa.io/get-pip.py \
  && python3 get-pip.py \
  && pip3 install pipenv \
  && mkdir /certs \
  && chown -R mitm:mitm /certs /pipenv \
  && sudo -u mitm pipenv install --three \
  && ln -s /pipenv/api $(sudo -u mitm pipenv --venv)/lib/python3.6/site-packages/

COPY start.sh /usr/local/bin
COPY start.py /pipenv
COPY api /pipenv/api
COPY flows /pipenv/flows

ENTRYPOINT ["/usr/local/bin/start.sh"]
EXPOSE 2222 5555
