# RIFO

This project is based on the algorithm described in the paper **[RIFO: Pushing the Efficiency of Programmable Packet Schedulers](https://arxiv.org/abs/2308.07442)** by *Habib Mostafaei, Maciej Pacut, Stefan Schmid*.

RIFO is a P4- and Python-based packet scheduler using dynamic rank normalization. It prioritizes lower-ranked packets when queue space is limited.

## 1. Basic Functionality
- Rank-based classification → every packet gets a rank.
- RIFO converts ranks into relative ranks, estimating whether they are "high", "low", or "medium".
- Normalization: checks where the received packet’s rank stands compared to previous ones.
- An extra field is required in the packet header: RIFO header that stores the rank.

## 2. Execution
```
sudo p4run
```

## 3. Packet Reception
Open h1 in a separate terminal:
```
mx h1
```
Once the h1 terminal appears, run the following to receive packets:
```
python receive_log.py
```

## 4. Packet Sending
Open h2 in a separate terminal:
```
mx h2
```
Once the h2 terminal appears, run the following to send packets:
- ```python send_one.py```
- ```python send_multiple.py```
- ```python send_dynamic.py```

The sender scripts are configured so that hi (i=2..10) hosts send packets to h1, and h1 sends to h2. **Each script can be run on any host, so sending from h2 to h1 also works.**

## 5. Reception and Sending
The following script starts ```receive_log.py``` on host h1 and writes the received packets to the terminal and the script_run/receiver.log file. Additionally, it starts ```send_dynamic.py``` on hosts h2 to h10 and writes the sent packets to the terminal and the script_run/sender_hi.log files.
```
./run_more_hosts.sh
```

## 6. RIFO Decision Logic
- Decision goal: whether the received packet should be admitted into the queue for forwarding.
- Principle: lower-ranked packets are prioritized.
  - If there is enough space in the queue, higher-ranked packets may be admitted.
  - If the queue is full, higher-ranked packets are dropped.

## 7. Algorithm Operation

![image](https://github.com/user-attachments/assets/0f9014af-e817-43ab-83c7-6561c90abbda)

### 7.1 Tracking
Tracking recent ranks.  
reg_min and reg_max store the smallest and largest ranks so far.  
These are occasionally reinitialized to keep the data fresh.
```
action reset_min_max(bit<16> rank) {
        reg_min.write(0, rank);
        reg_max.write(0, rank);
        reg_count.write(0, 1);
    }
```

### 7.2 Scoring
Score calculation
```
bit<16> rank_diff = hdr.rifo.rank - min_rank;
bit<16> range_val = max_rank - min_rank;
```
To calculate the position of the packet rank within the range and determine queue capacity:
- max capacity = B
- utilization = L
```
const bit<8> B = 5;
register<bit<8>>(1) queue_length; //current queue length (utilization)
```
Guaranteed admission buffer:  
A small part of the front of the queue is always reserved for immediate admission (k\*B).
```
const bit<8> kB = 3;
```

### Number of Hosts: 10
The simulation works most clearly with 10 hosts, since this way packets are dropped based on their ranks.

### Number of Sent Packets: 900
The send_dynamic.py script sends 100 packets, and this script is called by each of the 9 sending hosts.

### Packet Structure:
- After the IP header comes the RIFO header
- The RIFO header contains the rank
```
    ethernet_t ethernet;
    ipv4_t ipv4;
    rifo_t rifo;
```

Received packet:  
```
[893] Packet received with rank=55874 from 10.0.1.5 -> 10.0.1.1 on h1-eth0
```

Sent packet:  
```
[30] Packet sent with rank=52197 from 10.0.1.2 -> 10.0.1.1 on h2-eth0
```

The ```send_dynamic.py``` and ```receive_log.py``` scripts track how many packets were sent and received. For example, if 9 hosts send 100 packets each (9\*100=900), and 870 are received, then 30 packets were dropped due to having a rank that was too high.

## 8. Files

| Filename             | Description                                                                                                   |
|----------------------|---------------------------------------------------------------------------------------------------------------|
| ```rifo.p4```              | Full P4 implementation: header definitions, RIFO logic (rank-based drop/forward), register handling          |
| ```send_one.py```          | Sends one packet with rank 10                                                                                 |
| ```send_multiple.py```     | Sends 5 packets with different ranks                                                                          |
| ```send_dynamic.py```      | Sends 100 packets with random rank values between 0 and 65000                                                 |
| ```receive_log.py```       | Receiver-side logger: prints the `rank` value of incoming packets                                             |
| ```config.py```            | Contains network settings for the hosts (interface, IP and MAC addresses) for Scapy-based sending/receiving, and defines the custom RIFO protocol structure used by the sender and receiver Python scripts |
| ```p4app.json```           | Mininet topology with 10 hosts, each connected to the s1 switch                                               |
| ```s1-commands.txt```      | Commands for the forwarding table (where to send what)                                                        |
| ```log directory```        | p4 logs                                                                                                       |
| ```run_more_hosts.sh```    | Implements packet sending from multiple hosts                                                                 |
| ```script_run directory```      | Logs generated by run_more_hosts.sh                                                                           |