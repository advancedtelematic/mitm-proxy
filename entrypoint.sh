#!/bin/bash

set -xeuo pipefail


# set up the qemu network bridge
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


# generate the mitmproxy CA certificate
openssl genrsa -out /certs/mitmproxy.crt 2048
openssl req -x509 -newkey rsa:4096 -nodes -days 365 \
  -subj "/CN=${CERT_CN:-*}" \
  -keyout /certs/mitmproxy.key \
  -out /certs/mitmproxy.crt
cat /certs/mitmproxy.key /certs/mitmproxy.crt > /certs/mitmproxy-ca.pem


# start the qemu image in the background
qemu-system-x86_64 \
  -bios "${BIOS_FILE:-/qemu/u-boot-qemux86-64.rom}" \
  -drive file="${IMAGE_FILE:-/qemu/core-image-minimal-qemux86-64.otaimg}",if=ide,format=raw,snapshot=on \
  -m 128M \
  -nographic \
  -net user,hostfwd=tcp::2222-:22,restrict=off \
  -net nic,macaddr="${MAC:-CA-FE-$(jot -w%02X -s- -r 4 1 256)}",model=virtio \
  -net tap,ifname=tap0,script=no,downscript=no \
  &


# append the mitmproxy CA certificate to the device CA chain
SOTA_DIR=${SOTA_DIR:-"/var/sota"}
ROOT_CERT=${ROOT_CERT:-"root.crt"}
CLIENT_NAME=${CLIENT_NAME:-aktualizr}
CLIENT_CERT=${CLIENT_CERT:-"client.pem"}
CLIENT_KEY=${CLIENT_KEY:-"pkey.pem"}
CLIENT_OUT=${CLIENT_OUT:-"bundle.pem"}
SSH="ssh -p 2222 -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@localhost"
SCP="scp -P 2222 -o ConnectTimeout=10 -o StrictHostKeyChecking=no"

until ${SSH} true; do echo "Waiting for qemu..." && sleep 1; done
until ${SSH} "[[ -e ${SOTA_DIR}/${CLIENT_CERT} ]]"; do echo "Waiting for ${CLIENT_CERT}..." && sleep 5; done

${SSH} "mount -o rw,remount /usr"
${SSH} "cat ${SOTA_DIR}/${CLIENT_CERT} ${SOTA_DIR}/${CLIENT_KEY} > ${SOTA_DIR}/${CLIENT_OUT}"
${SCP} "root@localhost:${SOTA_DIR}/{${ROOT_CERT},${CLIENT_OUT}}" /certs
${SCP} "root@localhost:${SOTA_DIR}/${CLIENT_OUT}" /certs
${SCP} /certs/mitmproxy.crt root@localhost:/usr/share/ca-certificates
${SSH} "cat /usr/share/ca-certificates/mitmproxy.crt >> ${SOTA_DIR}/${ROOT_CERT}"
${SSH} "systemctl restart ${CLIENT_NAME}"
#${SSH} "echo 'mitmproxy.crt' >> /etc/ca-certificates.conf && /usr/sbin/update-ca-certificates"


# forward qemu traffic through the proxy
echo 1 > /proc/sys/net/ipv4/ip_forward
echo 0 | tee /proc/sys/net/ipv4/conf/*/send_redirects

iptables -t nat -A OUTPUT -o br0 -p tcp -m owner --uid-owner mitm -j ACCEPT
iptables -t nat -A OUTPUT -o br0 -p tcp -j REDIRECT --to-port 8080


## start the mitmproxy server
exec sudo -u mitm pipenv run \
  "${CMD:-mitmdump}" \
  --transparent \
  --host \
  --cadir=/certs \
  --upstream-trusted-ca="/certs/${ROOT_CERT}" \
  --client-certs="/certs/${CLIENT_OUT}" \
  --script /pipenv/entrypoint.py
