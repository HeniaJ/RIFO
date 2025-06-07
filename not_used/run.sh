#!/bin/bash
set -e

# Fordítás (ha szükséges)
p4c-bm2-ss --target bmv2 --arch v1model \
  --p4runtime-files rifo.p4info.txt \
  -o rifo.json \
  rifo.p4

# Tisztítás
sudo mn -c
sudo pkill -9 simple_switch_grpc || true

# SWITCH indítása P4 pipeline-nal, gRPC-vel
simple_switch_grpc \
  --device-id 0 \
  --log-file s1.log \
  --log-level debug \
  rifo.json \
  -- --grpc-server-addr 127.0.0.1:50051 &
sleep 2

# Mininet topológia indítása
sudo mn --custom topo.py --topo rifotopo --controller=remote --switch ovsbr,protocols=OpenFlow13
