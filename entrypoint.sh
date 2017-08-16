#!/bin/bash

set -euo pipefail


# set up the qemu network bridge
IP_DOCKER=$(ip addr show dev eth0 | grep "inet " | awk '{print $2}' | cut -f1 -d/)
IP_GATEWAY="$(echo ${IP_DOCKER} | cut -f1,2,3 -d\.).1"

brctl addbr br0
brctl addif br0 eth0
ifconfig br0 ${IP_DOCKER} netmask 255.255.0.0
ifconfig eth0 0.0.0.0 promisc up
route add default gw ${IP_GATEWAY} br0
tunctl -t tap0
brctl addif br0 tap0
ifconfig tap0 0.0.0.0 promisc up


# start the qemu image in the background
qemu-system-x86_64 \
  -bios ${BIOS_FILE:-/qemu/u-boot.rom} \
  -drive file=${IMAGE_FILE:-/qemu/core-image-minimal-qemux86-64.otaimg},if=ide,format=raw,snapshot=on \
  -m 1G \
  -nographic \
  -net user,hostfwd=tcp::2222-:22,restrict=off \
  -net nic,macaddr=${MAC:-$(echo CA-FE-$(jot -w%02X -s- -r 4 1 256))},model=virtio \
  -net tap,ifname=tap0,script=no,downscript=no \
  &


# generate the mitmproxy CA certificate
openssl genrsa -out /certs/mitmproxy.crt 2048
openssl req -x509 -newkey rsa:4096 -nodes -days 365 \
  -subj "/CN=${CERT_CN:-*.atsgarage.com}" \
  -keyout /certs/mitmproxy.key \
  -out /certs/mitmproxy.crt
cat /certs/mitmproxy.key /certs/mitmproxy.crt > /certs/mitmproxy-ca.pem


# append the mitmproxy CA certificate to the device CA chain
DEVICE_CA=${DEVICE_CA:-"/var/sota/ca.crt"}
DEVICE_PEM=${DEVICE_PEM:-"/var/sota/device.pem"}
SSH="ssh -p 2222 -o ConnectTimeout=1 -o StrictHostKeyChecking=no -o LogLevel=quiet root@localhost"
SCP="scp -P 2222 -o StrictHostKeyChecking=no -o LogLevel=quiet"

until ${SSH} true; do echo "Waiting for qemu..." && sleep 5; done
until ${SSH} "[[ -e ${DEVICE_PEM} ]]"; do echo "Waiting for ${DEVICE_PEM}..." && sleep 5; done

${SSH} "mount -o rw,remount /usr"
${SCP} /certs/mitmproxy.crt root@localhost:/usr/share/ca-certificates
${SCP} root@localhost:${DEVICE_CA} /certs
${SCP} root@localhost:${DEVICE_PEM} /certs
${SSH} "echo "mitmproxy.crt" >> /etc/ca-certificates.conf && /usr/sbin/update-ca-certificates"
${SSH} "cat /usr/share/ca-certificates/mitmproxy.crt >> ${DEVICE_CA}"


# forward qemu traffic through the proxy
echo 1 > /proc/sys/net/ipv4/ip_forward
echo 0 | tee /proc/sys/net/ipv4/conf/*/send_redirects

iptables -t nat -A OUTPUT -o br0 -p tcp -m owner --uid-owner mitm -j ACCEPT
iptables -t nat -A OUTPUT -o br0 -p tcp -j REDIRECT --to-port 8080


# start the mitmproxy server
exec sudo -u mitm pipenv run \
  ${CMD:-mitmproxy} \
  --transparent \
  --host \
  --cadir=/certs \
  --client-certs=/certs/device.pem \
  --upstream-trusted-ca=/certs/ca.crt \
  --script /pipenv/src/proxy.py
