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
**A forwarding table úgy van beállítva, hogy h1 h2-re, h2 meg h1-re küldjön.**


| Fájlnév            | Leírás                                                                                           |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| `rifo.p4`          | Teljes P4 implementáció: header definíciók, RIFO logika (rangalapú drop/admit), regiszterkezelés |
| `send_one.py`   | Egy csomag küldése         |
| `send_multiple.py` | Statikus rangú csomagok küldése egyik host-ról a másikra felé tesztelésre                                         |
| `send_dynamic.py`  | (opcionális) Több száz véletlen rangú csomag küldése stresszteszthez                             |
| `receive_log.py`     | Fogadóoldali naplózó: érkező csomagok `rank` értékét kiírja                                |
| `config.log`          | Host beállítások küldéshez és fogadáshoz                                                       |
| `p4app.json`          | Mininet topológia H1 ↔ S1 ↔ H2, 2 porttal                                                        |
| `s1-commands.txt`          | Forwarding table-höz parancsok (mit hova küldjön)                                                    |
| `log mappa`           | Logok                                |

