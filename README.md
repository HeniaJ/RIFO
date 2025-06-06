# RIFO

1. futtatás
```
sudo p4run
```

2. csomagküldés (mininetben)
```
h1 python3 send_multiple.py
```

3. csomag fogadás (mininetben)
```
h2 python3 h2_logger.py
```

Fájlnév	Leírás
| Fájlnév            | Leírás                                                                                           |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| `rifo.p4`          | Teljes P4 implementáció: header definíciók, RIFO logika (rangalapú drop/admit), regiszterkezelés |
| `rifomod.py`    | Megpróbáltam táblával kezelni a portokat (kísérleti)                                 |
| `send_one.py`   | Egy csomag küldése         |
| `send_multiple.py` | Statikus rangú csomagok küldése H1 → H2 felé tesztelésre                                         |
| `send_dynamic.py`  | (opcionális) Több száz véletlen rangú csomag küldése stresszteszthez                             |
| `h2_logger.py`     | Fogadóoldali naplózó: H2-re érkező csomagok `rank` értékét kiírja                                |
| `p4app.json`          | Mininet topológia H1 ↔ S1 ↔ H2, 2 porttal                                                        |
| `log mappa`           | Logok                                |


# Szerintem ez nem kell, ami ez után van:

Fájlnév	Leírás
| Fájlnév            | Leírás                                                                                           |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| `rifo.p4`          | Teljes P4 implementáció: header definíciók, RIFO logika (rangalapú drop/admit), regiszterkezelés |
| `controller.py`    | Pipeline feltöltése P4Runtime-on keresztül (egyszeri setup)                                      |
| `controller2.py`   | **(Bővített)** Vezérlő: pipeline betöltés + regiszterek lekérdezése (még nem működik)            |
| `send_multiple.py` | Statikus rangú csomagok küldése H1 → H2 felé tesztelésre                                         |
| `send_dynamic.py`  | (opcionális) Több száz véletlen rangú csomag küldése stresszteszthez                             |
| `h2_logger.py`     | Fogadóoldali naplózó: H2-re érkező csomagok `rank` értékét kiírja                                |
| `topo.py`          | Mininet topológia H1 ↔ S1 ↔ H2, 2 porttal                                                        |
| `run.sh`           | Teljes rendszerindítás: fordítás, switch indítás, Mininet indítás                                |

# Mi kell ahhoz, hogy működjön a RIFO rendszer?

1. P4 toolchain

git clone https://github.com/p4lang/p4c.git

cd p4c

mkdir build && cd build

cmake ..

make -j$(nproc)

sudo make install

2. BMv2 (behavioral model v2)

git clone https://github.com/p4lang/behavioral-model.git

cd behavioral-model

./install_deps.sh

./autogen.sh

./configure --with-p4runtime

make -j$(nproc)

sudo make install

3. Python könyvtárak

pip3 install grpcio grpcio-tools protobuf scapy


# Futtatás lépései

1 Előkészítés

sudo mn -c

sudo pkill -9 simple_switch_grpc

2 Fordítás (automatikusan benne van a run.sh-ban)

p4c-bm2-ss --target bmv2 --arch v1model \
  --p4runtime-files rifo.p4info.txt \
  -o rifo.json \
  rifo.p4
  
3 Switch és Mininet indítása

chmod +x run.sh

./run.sh

Ez elindítja:

simple_switch_grpc 127.0.0.1:50051-en

Mininet topológiát rifotopo névvel

4 Vezérlő betöltése (új terminálban)

python3 controller.py

Ha sikeres:

Pipeline loaded successfully.

5 Csomagküldés H1-ről

mininet> h1 python3 send_multiple.py

6 Naplózás H2-n (külön terminálon)

mininet> h2 python3 h2_logger.py

Minden fogadott csomag rank értékét kiírja.
