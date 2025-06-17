#!/bin/bash
mkdir -p script_run

{
echo "[+] Starting receiver on h1..."
mx h1 python3 receive_log.py &
sleep 5

for i in $(seq 2 15)
do
    host="h$i"
    echo "[+] Starting sender on $host..."
    mx $host python3 send_dynamic.py &
done

wait
} &> script_run/run_more_host.log