# tuf-mitm-proxy

Script that does TUF related manipulations via `mitmproxy`.

## Usage

### Building and running the Docker image

In the project root run `make image` to build the docker image. This will install Python 3.6 plus all project dependencies. It will also copy over the `api/` and `flows/` directory and `start.sh` script for starting the API.

The `start.sh` script will boot a QEMU image containing the client to test, copy a root certificate into this image and forward all bridged TCP traffic to `mitmproxy`. The image will be booted in snapshot mode so no changes to the image itself will be persisted.

To start this process run `make start`. You will need to set the `IMAGE_DIR` environment variable to the directory containing the QEMU image.

By default, it will look for an image named `core-image-minimal-qemux86-64.otaimg` and a bios file name `u-boot-qemux86-64.rom`. These values can be overridden by setting the `IMAGE_FILE` and `BIOS_FILE` environment variables passed to the bootstrap script when starting the image.

### HTTP API

Send a `GET` request to `/available` or `/running` to see the available flows or currently running flow respectively.

Send a `PUT` request to `/start/<name>` to start a new flow (where `<name>` is the flow name). To stop the currently running flow, send a `PUT` request to `/stop`.

## License

This work is licensed under the MPL2 license.
