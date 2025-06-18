# RIFO

## 1. futtatás
```
sudo p4run
```

## 2. csomagküldés

külön terminálban:
```
mx h1
```
feljön h1 terminálja, akkor lehet:
- ```python send_one.py```
- ```python send_multiple.py```
- ```python send_dynamic.py```

## 3. csomag fogadás
külön terminálban:
```
mx h2
```
feljön h2 terminálja, akkor lehet:
```
python receive_log.py
```

***Mindegyik script futtatható mindegyik host-on, tehát ha h2-ről köldünk h1-re az is működik.***
**A forwarding table úgy van beállítva, hogy mind a 10 host a h1-re küldjön csomagokat.**


| Fájlnév            | Leírás                                                                                           |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| `rifo.p4`          | Teljes P4 implementáció: header definíciók, RIFO logika (rangalapú drop/admit), regiszterkezelés |
| `send_one.py`      | Egy csomag küldése                                                                               |
| `send_multiple.py` | Statikus rangú csomagok küldése egyik host-ról a másik felé tesztelésre                          |
| `send_dynamic.py`  | (opcionális) Több száz véletlen rangú csomag küldése stresszteszthez                             |
| `receive_log.py`   | Fogadóoldali naplózó: érkező csomagok `rank` értékét kiírja                                      |
| `config.log`       | Host beállítások küldéshez és fogadáshoz                                                         |
| `p4app.json`       | Mininet topológia 10 hosttal                                                                     |
| `s1-commands.txt`  | Forwarding table-höz parancsok (mit hova küldjön)                                                |
| `log mappa`        | Logok                                                                                            |
| `run_more_hosts.sh`| Több host csomagküldésének megvalósítása                                                         |
| `config.py`        | Gép hálózati interfészének megfelelő konfigurációja                                              |
| `receive_sync.py`  | Párhuzamos csomagfeldolgozás                                                                     |

### Hostok száma: 10 
Ha ennél több host lenne, azok túlságosan sok csomagot küldenének, 
amitől a program már ingress fázis előtt eldobna csomagokat

Leglátványosabban 10 hosttal működik a szimuláció, mivel így a rangok alapján dobja el a csomagokat.

### Küldött csomagok száma: 900 
A send_dynamic.py scriptben 100 csomagot küld el, és ezt a scriptet mind a 9 csomagküldő host meghívja.

### Csomag felépítése:
* IP fejléc után RIFO fejléc
* RIFO fejléc a rangot tartalmazza
* ```
    ethernet_t ethernet;
    ipv4_t ipv4;
    rifo_t rifo;
```
