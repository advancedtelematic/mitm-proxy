# tuf-mitm-proxy

This project enables manipulation of [TUF flows](https://theupdateframework.github.io) between the [SOTA Client](https://github.com/advancedtelematic/aktualizr) and [SOTA Server](http://genivi.github.io/rvi_sota_server/) via [mitmproxy](https://mitmproxy.org).

## Usage

Run `make` to see the available Makefile commands.

### Available proxy flows

The `flows/` directory contains the individual `mitmproxy` flows that will manipulate the TUF metadata traffic. An HTTP API is started inside Docker to switch between the flows in this directory.

### Starting the transparent proxy

To boot a new client QEMU image run `make start` with the `IMAGE_DIR` environment variable set.

By default, `IMAGE_DIR` should contain a QEMU image named `core-image-minimal-qemux86-64.otaimg` and a BIOS file named `u-boot-qemux86-64.rom`, though these can be overridden by setting `IMAGE_FILE` and `BIOS_FILE` respectively.

### Controlling the proxy

Send a `GET` request to `/available` or `/running` to see the available flows or currently running flow respectively.

Send a `PUT` request to `/start/<name>` to start a new flow (where `<name>` is the flow name), or send a `PUT` request to `/stop` to stop the currently active flow.
