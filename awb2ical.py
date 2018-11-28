#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#
# (c) Michael Strecke, 2018
# This program is released into public domain

import datetime
import random
import json
import re
import urllib.request

# Name der Konfigurationsdatei
INI_FILENAME = "awb2ical.cfg"

# Name der Ausgabedatei
# %s wird durch Jahreszahl ersetzt
ICAL_OUTFNM = '/tmp/awb%s.ics'


# Umbenennung der Termine
# Name in JSON -> Name im Termin

INFO_TRANSLATE = {
    'grey': 'Rest',
    'blue': 'Papier',
    'brown': 'Bio',
    'red': 'Arzt',
    'wertstoff': 'Wert',     # gelbe Tonne
}

def read_simple_config_file(filename):
    """ Einfacher Konfigurationsdateiparser

    :param filename: Dateiname
    :return: dict mit Werten (Schlüssel in Kleinbuchstaben
    """
    # Aufbau:
    #
    # SCHLÜSSEL=Wert
    # Kommentarzeilen beginnt mit "#"
    # Leerzeilen werden ignoriert

    erg =  {}

    with open(filename, "r", encoding="utf8") as ein:
        while True:
            line = ein.readline()
            if line == '':            # EOF
                break
            if line.startswith("#"):  # Kommentar
                continue

            line = line.rstrip()
            if line == '':
                continue              # Leerzeile

            ma = re.search("^(.+?)=(.+)", line)
            assert ma is not None, "Unbekante Syntax: " + line

            erg[ ma.group(1).strip().lower() ] = ma.group(2).strip()

    return erg


default_timezone= 'Europe/Luxembourg'

def datetime2txt(dt):
    """ Ausgabe eines Datetime Elements mit Zeitzone ("Z" = GMT)

    :param dt: datetime mit Zeitzone
    :return: String für ICAL
    """
    # -> 20150227T141115Z
    return "%04d%02d%02dT%02d%02d%02dZ" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

def date_or_datetime2txt(dt):
    if type(dt) is datetime.date:
        return "DATE:%04d%02d%02d" % (dt.year, dt.month, dt.day)
    if type(dt) is datetime.datetime:
        return "DATE-TIME;TZID=%s:%04d%02d%02dT%02d%02d%02d" % (default_timezone, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

def ausgabe_wenn_nicht_none(out, string, value=None, convfunc=None):
    """ Zeile ausgeben, wenn Wert nicht None ist

    :param out: Handle für Ausgabedatei
    :param string: auszugebender Text
    :param value: zu testender und auszugebender Wert
    :param convfunc: Funktion Wert -> String (oder None)
    :return:
    """
    if value is not None:
        out.write(string)
        if convfunc is None:
            convfunc = str
        out.write('%s\n' % convfunc(value))

def get_random_hexbytes(count):
    """ Zufahlszahlen für iCAL UID

    :param count: Anzahl an Bytes
    :return: Anzahl * 2 Hex-Nibbles
    """
    s = ''
    for x in range(count):
        s += "%02x" % random.randrange(256)
    return s

def now():
    return datetime.datetime.now()

class vevent:
    """ Ein Termin

    """
    def __init__(self):
        self.created = None                # erstellt um
        self.uid = None                    # eindeutige ID (Zufallszahl)
        self.last_modified = None          # letzte Änderung
        self.dt_stamp = None               # Zeitstempel
        self.summary = None                # der angezeigte Text
        self.dt_start = None               # Termin: Startdatum/zeit
        self.dt_end = None                 # Termin: Enddatum/zeit

    def new_event(self, d_from, d_until, summary):
        """ Termin mit Info füllen

        :param d_from: Startzeitpunkt
        :param d_until: Endzeitpunkt
        :param summary: anzuzeigender Text
        :return:
        """
        just_now = now()

        self.created = just_now
        self.last_modified = just_now
        self.dt_stamp = just_now
        self.summary = summary
        self.dt_start = d_from
        self.dt_end = d_until
        self.uid = get_random_hexbytes(12)

    def _tocal(self, out):
        """ Ausgabe im iCAL-Format

        :param out: Handle der Ausgabedatei
        :return:
        """
        out.write('BEGIN:VEVENT\n')
        ausgabe_wenn_nicht_none(out, 'UID:', self.uid)
        ausgabe_wenn_nicht_none(out, 'LAST-MODIFIED:', self.last_modified, datetime2txt)
        ausgabe_wenn_nicht_none(out, 'DTSTAMP:', self.dt_stamp, datetime2txt)
        ausgabe_wenn_nicht_none(out, 'SUMMARY:', self.summary)
        ausgabe_wenn_nicht_none(out, 'DTSTART;VALUE=', self.dt_start, date_or_datetime2txt)
        ausgabe_wenn_nicht_none(out, 'DTEND;VALUE=', self.dt_end, date_or_datetime2txt)
        out.write('END:VEVENT\n')

class vcalendar:
    """ Der Kalender

    """
    def __init__(self):
        self.liste = []

    def _tocal(self, out):
        """ Ausgabe des Kalenders im iCAL-Format

        :param out: Handle der Ausgabedatei
        :return:
        """

        # Header
        out.write('BEGIN:VCALENDAR\nVERSION:2.0\nCALSCALE:GREGORIAN\n')
        # Ausgabe der Termine
        for ele in self.liste:
            ele._tocal(out)
        # Footer
        out.write('END:VCALENDAR\n')

    def append(self, entry):
        """ Termin zum Kalender hinzufügen

        :param entry: Termin (vevent)
        :return:
        """
        self.liste.append(entry)

if __name__ == "__main__":
    cfg = read_simple_config_file(INI_FILENAME)

    year = cfg["jahr"]
    streetcode = cfg["strasse"]
    building = cfg["hausnummer"]

    dataout_fnm = ICAL_OUTFNM % year
    APIQUERY = f"https://www.awbkoeln.de/api/calendar?building_number={building}&street_code={streetcode}&start_year={year}&end_year={year}&start_month=1&end_month=12&form=json"

    print("API Query:", APIQUERY)

    # Daten über AWS API lesen
    data = urllib.request.urlopen(APIQUERY).read()

    # Ergebnis zu Zu Debug-Zwecken protokollieren
    # open("/tmp/jsondata.txt", "wb").write(data)
    # data = open("/tmp/jsondata.txt", "rb").read()

    jsondata = json.loads(data)
    jsonevents = jsondata.get("data")
    assert jsonevents is not None, "Datenformat hat sich geändert"

    assert len(jsonevents)>0, "Keine Daten zurückgemeldet. Stimmt das Jahr (%s)?" % year

    # Liste der Ereignisse von JSON in vevents umwandeln
    liste = []
    for event in jsonevents:
        da = datetime.date(year = event['year'], month=event['month'], day=event['day'])
        info =  INFO_TRANSLATE.get(event['type'], event['type'])
        liste.append( (da, info) )
        assert info is not None

    # Liste sortieren
    liste.sort()

    # Termine zusammenfassen
    # Mehrere Leerungen an einem Tag -> zu einem Termin

    conslist = []
    lastdat = None
    lastele = None
    for x in liste:
        datum, info = x
        if x[0] != lastdat:
            # neuer Eintrag
            lastdat = datum
            lastele = [ datum, [ info ] ]
            conslist.append( lastele )
        else:
            # zusätzliche Info zu letztem Eintrag hinzufügen
            lastele[1].append( info )

    # Zusammengefasste Liste in einen Kalender umwandeln
    cal = vcalendar()
    for x in conslist:
        datum_start, infolist = x
        datum_ende = datum_start + datetime.timedelta(days=1)

        ve = vevent()
        ve.new_event(datum_start, datum_ende, "/".join(infolist))
        cal.append(ve)

    # Liste ausgeben
    with open(dataout_fnm, "w") as f:
        cal._tocal(f)

    # Infos ausgeben

    print("Ausgabedatei:", dataout_fnm)
    print("%s Einträge" % len(liste))
    print("%s zusammengefasste Einträge" % len(conslist))
