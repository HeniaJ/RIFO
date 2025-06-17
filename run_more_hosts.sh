#!/bin/bash
echo "[+] Starting receiver on h1..."
mx h1 python3 receive_log.py &
sleep 5

for host in h2 h3 h4 h5
do
    echo "[+] Starting sender on $host..."
    mx $host python3 send_dynamic.py &
done

wait