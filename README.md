# RIFO

## 1. Alap működés
* Rang alapú osztályozás --> minden csomag kap egy rangot.
* RIFO a rangokat relatív rangokra alakítja át, megbecsüli hogy "nagy", "kicsi" vagy "közepes".
* Normalizálás: megvizsgálja hogy a kapott csomag rangja hol helyezkedik el az eddigiekhez képest.
* Extra mezőre van szükség a csomag fejlécében: RIFO fejléc ami tárolja a rangot.

## 2. Futtatás
```
sudo p4run
```

## 3. Csomag fogadás

Külön terminálban h1 megnyitása:
```
mx h1
```
Amikor feljön h1 terminálja, akkor futtathatjuk a csomag fogadáshoz:
```
python receive_log.py
```

## 4. Csomag küldés

Külön terminálban h2 megnyitása:
```
mx h2
```
Amikor feljön h2 terminálja, futtathatjuk a csomag küldéshez:
- ```python send_one.py```
- ```python send_multiple.py```
- ```python send_dynamic.py```

A sender scriptek úgy vannak beállítva, hogy hi (i=2..10) host a h1-re küldjön csomagokat, h1 pedig h2-re. ***Mindegyik script futtatható mindegyik host-on, tehát ha h2-ről köldünk h1-re az is működik.***

## 5. Fogadás és küldés

A következő script h1 hoston elindítja a ```receive_log.py```-t és a kapott csomagokat kiírja a terminálba és a script_run/receiver.log fájlba. Ezenkívül elindítja a h2...h10 hostokon a ```send_dynamic.py```-t, és az elküldött csomagokat kiírja a terminálba és a script_run/sender_hi.log fájlokba.
```
./run_more_hosts.sh
```

## 6. RIFO döntési logika

* Döntés témája: kapott csomagot a program beengedje-e a sorba továbbküldésre.
* Elv: alacsonyabb rangú csomagok előnyben.
   * Ha a sorban van elég hely magasabb rangú csomagot is beenged.
   * Ha a sor megtelik a magasabb rangú csomagokat dobja el.

## 7. Algoritmus működése

![image](https://github.com/user-attachments/assets/0f9014af-e817-43ab-83c7-6561c90abbda)

#### 6.1 Tracking
Legutóbbi rangok nyomonkövetése. \
reg_min, reg_max tárolják az eddigi legkisebb és legnagyobb rangokat. \
Ezek időnként újrainicializálódnak az adatok frissentartása érdekében.
```
action reset_min_max(bit<16> rank) {
        reg_min.write(0, rank);
        reg_max.write(0, rank);
        reg_count.write(0, 1);
    }
```

#### 6.2 Scoring
Pontszám számolása
```
bit<16> rank_diff = hdr.rifo.rank - min_rank;
bit<16> range_val = max_rank - min_rank;
```
Csomag rangjának tartományon belüli pozíciójának kiszámolásához sor kapacitásának meghatározása
* max kapacitás = B
* kihasználtság = L
```
const bit<8> B = 5;
register<bit<8>>(1) queue_length; //aktualis sorhossz (kihasználtság)
```
Garantált beengedési puffer: \
Sor elejéből egy kis rész mindig fenn van tartva azonnali beengedésre (k*B).
```
const bit<8> kB = 3;
```

### Hostok száma: 10 
Leglátványosabban 10 hosttal működik a szimuláció, mivel így a rangok alapján dobja el a csomagokat.

### Küldött csomagok száma: 900 
A send_dynamic.py scriptben 100 csomagot küld el, és ezt a scriptet mind a 9 csomagküldő host meghívja.

### Csomag felépítése:
* IP fejléc után RIFO fejléc
* RIFO fejléc a rangot tartalmazza
```
    ethernet_t ethernet;
    ipv4_t ipv4;
    rifo_t rifo;
```

Megkapott csomag:
```
[893] Packet received with rank=55874 from 10.0.1.5 -> 10.0.1.1 on h1-eth0
```

Elküldött csomag:
```
[30] Packet sent with rank=52197 from 10.0.1.2 -> 10.0.1.1 on h2-eth0
```

A ```send_dynamic.py``` és a ```receive_log.py``` számon tartják, hogy mennyi csomagot küldtek, és fogadtak, így például ha 9*100=900 csomagot elküldött 9 host, és 870 érkezett meg, akkor 30-at eldobtunk, mert túl magas volt a rangja.

## 8. Fájlok

| Fájlnév            | Leírás                                                                                           |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| `rifo.p4`          | Teljes P4 implementáció: header definíciók, RIFO logika (rangalapú drop/forward), regiszterkezelés |
| `send_one.py`      | Egy csomag küldése 10-es ranggal                                                                              |
| `send_multiple.py` | 5 csomag küldése különböző rangokkal                          |
| `send_dynamic.py`  | 100 csomag küldése véletlenszerű ranggal 0 és 65000 között                             |
| `receive_log.py`   | Fogadóoldali naplózó: érkező csomagok `rank` értékét kiírja                                      |
| `config.py`       | Tartalmazza a hostok hálózati beállításait (interfész, IP- és MAC-címek) a Scapy-alapú küldéshez és fogadáshoz, valamint definiálja a RIFO nevű egyedi protokollstruktúrát, amiket a fogadó és küldő python scriptek fel tudnak használni.                                                       |
| `p4app.json`       | Mininet topológia 10 hosttal, ahol mindegyik s1 switch-el van összekötve.                                                                     |
| `s1-commands.txt`  | Forwarding table-höz parancsok (mit hova küldjön)                                                |
| `log mappa`        | p4 logok                                                                                            |
| `run_more_hosts.sh`| Több host csomagküldésének megvalósítása                                                         |
| `script_run mappa`| run_more_hosts.sh logok                                                     |
