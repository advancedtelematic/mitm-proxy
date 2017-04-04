FROM mitmproxy/mitmproxy:2.0

COPY ./ /src/tuf-mitm-proxy

RUN apk add --no-cache --virtual gcc && \
    apk add --no-cache --virtual python3-dev && \
    apk add --no-cache --virtual musl-dev 

RUN python3 -m ensurepip && \
    LDFLAGS=-L/lib pip3 install -r /src/tuf-mitm-proxy/requirements.txt

RUN apk del --purge \
        gcc \
        python3-dev \
        musl-dev && \
    rm -rf ~/.cache/pip /tmp/*

WORKDIR /src/tuf-mitm-proxy/scripts

CMD ["mitmproxy"]
