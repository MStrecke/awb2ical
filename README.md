# Abfuhrkalender der AWB Köln als iCal-Datei

*This utility is only useful for people living in Cologne, Germany.*

## Zweck

Die Abfallwirtschaftsbetriebe (AWB) in Köln veröffentlichen seit Jahren ihren 
Abfuhrkalender auch online (https://www.awbkoeln.de/) - in früheren Jahren
sogar als ausdruckbares PDF.

Leider gab es nie die Möglichkeit, die Termine in eine Kalender-App einzulesen.

Dieses Skript erzeugt eine iCal-Datei, die dies ermöglicht.

Hierzu fragt es eine API der AWB ab. Dazu benötigt es drei Angaben, die es aus 
der Konfigurationsdatei `awb2ical.cfg` einliest.

| Variable | Bedeutung |
| -------- | --------- |
| JAHR | Jahr:  1.1. bis 31.12. |
| STRASSE | Straßen-Code, siehe unten |
| HAUSNUMMER | Hausnummer des Gebäudes eventuell mit Zusatz |

### Straßen-Code und Hausnummer

Nachdem man auf der Website der AWB die Adresse für den Abfuhrkalender eingegeben 
hat, erscheint eine weitere Seite mit einer Monatsübersicht und einem Icon "Kalender drucken".

Wenn man den Zeiger über dieses Icon bringt, erscheint in der Fußleiste die zugehörige  Link.  

Im Zweifelsfall kann man diese mit einem Rechtsklick und der Option "Link-Adresse kopieren" 
in den Zwischenspeicher kopieren, dann in einem Textprogramm einfügen und dort 
untersuchen.

In dieser Link befindet sich irgendwo der Parameter `sensis_strassen_nr=XXXX`.
Dabei ist XXXX der gesuchte Straßen-Code. 

Die Hausnummer ist in `sensis_haus_nr=YYYY` zu sehen, wobei YYYY die Hausnummer ist. 
Diesen Parameter sollte besonders dann geprüft werden, wenn es Adresszusätze gibt, 
z.B. "2c", "15a".

:warnung: Die AWB können die API natürlich jederzeit ändern und dieses Programm 
unbrauchbar machen.

# Vorgehensweise

* Kopie von `awb2ical-example.cfg` erzeugen und nach `awb2ical.cfg` umbenennen.
* AWB-Seite besuchen, Adresse eingeben und Werte für Straßen-Code und Hausnummer aus 
  der Link notieren.
* Werte in `awb2ical.cfg` eintragen.
* `awb2ical.py` aufrufen
* Datei `/tmp/awb2019.ics` (2020, 2021, ...) in Kalender einlesen.  

# Hinweise für Programmierer

URL der Abfrage:

```
f"https://www.awbkoeln.de/api/calendar?building_number={building}&street_code={streetcode}&start_year={year}&end_year={year}&start_month=1&end_month=12&form=json"
```

Format der JSON-Antwort 

```json
{"data":[
    {"day":1,
     "month":8,
     "year":2018,
     "type":"blue"              # blue, grey, wertstoff
   },
   {"day":3,
    "month":9,
    "year":2018,
    "type":"blue"              # blue, grey, wertstoff
   },
   ...

]}
```
