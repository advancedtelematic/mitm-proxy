#!/bin/bash

set -euo pipefail


info() {
  echo -e "\033[0;31m$1\033[0m"
}

info "Setting up the qemu network bridge..." && {
  SUBNET="$(ip addr show eth0 | grep 'inet ' | awk '{print $2}')"
  GATEWAY="$(ip route list 0/0 | awk '{print $3}')"

  ip link add name br0 type bridge
  ip link set up br0
  ip addr flush dev eth0
  ip addr add "$SUBNET" dev br0
  route add default gw "$GATEWAY"

  ip tuntap add dev tap0 mode tap
  ip link set tap0 promisc on
  ip link set master br0 dev tap0
  ip link set master br0 dev eth0
}

info "Generating man-in-the-middle certificates..." && {
  openssl genrsa -out /certs/mitmproxy.crt 2048
  openssl req -x509 -newkey rsa:4096 -nodes -days 365 \
    -subj "/CN=${CERT_CN:-*}" \
    -keyout /certs/mitmproxy.key \
    -out /certs/mitmproxy.crt
  cat /certs/mitmproxy.key /certs/mitmproxy.crt > /certs/mitmproxy-ca.pem
}

info "Starting the client qemu image..." && {
  qemu-system-x86_64 \
    -bios "${BIOS_FILE:-/qemu/u-boot-qemux86-64.rom}" \
    -drive file="${IMAGE_FILE:-/qemu/core-image-minimal-qemux86-64.otaimg}",if=ide,format=raw,snapshot=on \
    -m 128M \
    -nographic \
    -net user,hostfwd=tcp::2222-:22,restrict=off \
    -net nic,macaddr="${MAC:-CA-FE-$(jot -w%02X -s- -r 4 1 256)}",model=virtio \
    -net tap,ifname=tap0,script=no,downscript=no \
    &
}

info "Fetching the mutual TLS certificates..." && {
  QEMU_HOST=${QEMU_HOST:-"root@localhost"}
  QEMU_PORT=${QEMU_PORT:-"2222"}
  SSH_OPTS=${SSH_OPTS:-"-o ConnectTimeout=10 -o StrictHostKeyChecking=no"}
  SSH="ssh -p ${QEMU_PORT} ${SSH_OPTS} ${QEMU_HOST}"
  SCP="scp -P ${QEMU_PORT} ${SSH_OPTS}"

  SOTA_DIR=${SOTA_DIR:-"/var/sota"}
  ROOT_CERT=${ROOT_CERT:-"root.crt"}
  CLIENT_NAME=${CLIENT_NAME:-"aktualizr"}
  CLIENT_CERT=${CLIENT_CERT:-"client.pem"}
  CLIENT_KEY=${CLIENT_KEY:-"pkey.pem"}

  until ${SSH} true; do info "Waiting for qemu..." && sleep 1; done
  until ${SSH} "[[ -e ${SOTA_DIR}/${CLIENT_KEY} ]]"; do info "Waiting for ${CLIENT_KEY}..." && sleep 5; done

  ${SSH} "mount -o rw,remount /usr"
  ${SSH} "cat >> ${SOTA_DIR}/${ROOT_CERT}" < /certs/mitmproxy.crt
  ${SSH} "systemctl restart ${CLIENT_NAME}"

  ${SCP} "${QEMU_HOST}:${SOTA_DIR}/{${ROOT_CERT},${CLIENT_CERT},${CLIENT_KEY}}" /certs
  cat /certs/{"${CLIENT_CERT}","${CLIENT_KEY}"} > /certs/bundle.pem
}

info "Forwarding qemu traffic to mitmproxy..." && {
  echo 1 > /proc/sys/net/ipv4/ip_forward
  echo 0 | tee /proc/sys/net/ipv4/conf/*/send_redirects

  iptables -t nat -A OUTPUT -o br0 -p tcp -m owner --uid-owner mitm -j ACCEPT
  iptables -t nat -A OUTPUT -o br0 -p tcp -j REDIRECT --to-port 8080
}

info "Starting the API..." && {
  exec sudo -u mitm \
    pipenv run python3 /pipenv/start.py \
    --http.host="${HTTP_HOST:-0.0.0.0}" \
    --http.port="${HTTP_PORT:-5555}" \
    --flow.root="${FLOW_ROOT:-/pipenv/flows}" \
    --flow.initial="${FLOW_INITIAL:-random_sig}" \
    --mitm.cadir=/certs \
    --mitm.upstream_trusted_ca="/certs/${ROOT_CERT}" \
    --mitm.client_certs="/certs/bundle.pem"
}
