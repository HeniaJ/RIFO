#!/bin/bash
mkdir -p script_run

# h1 fogado hosztra beerkezett csomagok logjainak eltarolasa
echo "[+] Starting receiver on h1..."
mx h1 python3 receive_log.py 2>&1 | tee script_run/receiver.log &

sleep 5

# 9 hoszt kuldi a csomagokat parhuzamosan
for i in $(seq 2 10)
do
    host="h$i"
    echo "[+] Starting sender on $host..."
    mx $host python3 send_dynamic.py 2>&1 | tee script_run/sender_$host.log &
done

wait
