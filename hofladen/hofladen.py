#!/bin/python3

import sys
from os.path import exists
import geocoder
import geojson
from csv import reader
from pprint import pformat

from hofladen.models import Hofladen

LADENPOS = 1

class hofladen():
    def __init__(self, csv_name="", geo_json="", TEST=False, verbose=0):
        """
            Die Class soll alle Funktion vom Erzeugen eines neuen Hofladens
            bis zum Erzeugen einer GEO-JSON Struct für das WWW-GUI
            abbilden.
            Für die Initialisierung müssen die Parameter csv_name und geo_json
            gegeben sein.
            Für das GUI müssen diese leer sein!
        """
        if csv_name and not exists(csv_name):
            print("ERROR: Die CSV_Datei: '%s' existiert nicht" % csv_name)
            sys.exit(1)
        self.csv_name = csv_name
        if geo_json and not exists(geo_json):
            print("ERROR: Die GEO-JSON_Datei: '%s' existiert nicht" % geo_json)
            sys.exit(1)
        self.geo_json  = geo_json
        self.TEST     = TEST
        self.verbose  = verbose

        self.column = {}
        self.rubriken = []

        self.geo_info = {}
    
        if geo_json:
            self.__init_geo_json__()

    def __init_geo_json__(self):
        """
            Lies die GEOJson Datei ein
        """
        with open(self.geo_json) as fd:
            self.geo_struct = geojson.load(fd)

        #
        # Erzeuge ein Dict mit den IDs in dem die Koordinate als
        # String enthalten ist
        #
        i = 0
        for geo_pos in self.geo_struct['features']:
            self.geo_info[geo_pos['properties']['fid']] = {
                'id'         : geo_pos['properties']['fid'],
                'coordinate' : "%s, %s" % (
                    geo_pos['geometry']['coordinates'][0],
                    geo_pos['geometry']['coordinates'][1]),
                'geo_elem_pos' : i,
                }
            i += 1

    def __init_rubriken__(self, first=False, second=False, laden={}):
        """
            Initialisiere die Rubriken aus der ersten Zeilen des
            SpreadSheets
        """
        if first and laden[LADENPOS] == 'Name':
            # Vanessas Spreadsheet hat unschöne Überschriften
            # die in 2 Zeilen aufgeteilt sind
            #   Bsp.
            # Obst,,,,Bienenprodukte,,
            # Beere,Apfel,Birne,....,Honig,Propolis
            #
            # D.h. aus der ersten Zeile müssen wir die Überschriften
            # ermitteln und aus der Folgezeile die
            #    Unterkategorie
            bio_found = False
            for p in range(len(laden)):
                if laden[p] == 'Bio' or bio_found:
                    bio_found = True
                    if not laden[p]:
                        continue
                    self.rubriken.append(
                        { 'name' : laden[p],
                          'pos'  : p,
                          'unterrubrik' : []
                        } )
                else:
                    self.column[laden[p]] = p

        if second:
            # behandle die Rubriken
            print("rubriken: %s" % pformat(self.rubriken))
            print("column: %s" % pformat(self.column))
            rubrik = 0
            act_rubrik = 0
            for p in range(len(laden)):
                if rubrik < len(self.rubriken) and \
                   p == self.rubriken[rubrik]['pos']:
                    act_rubrik = rubrik
                    rubrik += 1
                if laden[p]:
                    self.rubriken[act_rubrik]['unterrubrik'].append(laden[p])
            print("rubriken: %s" % pformat(self.rubriken))

    def create_new_geo_json_elem(self, hofladen):
        """
            Generiere ein neues Feature in der GEO-Json Datei
            Also einen neuen Hof
        """
        feature = {
            'geometry' : {
                "coordinates" : self.get_geo_coordinate(hofladen),
                "type" : "Point",
            },
            'properties' : {
                'fid' : hofladen['id'],
            },
            'type': 'Feature',
        }
        self.geo_info[hofladen['id']] = {
            'id'         : hofladen['id'],
            'coordinate' : "%s, %s" % (
                feature['geometry']['coordinates'][0],
                feature['geometry']['coordinates'][1]),
            'geo_elem_pos' : len(self.geo_struct['features']),
        }
        self.geo_struct['features'].append(feature)
        # und jetzt setz die übrigen Properties
        self.update_geo_json_elem(hofladen)

    def update_geo_json_elem(self, hofladen):
        """
            Setz die Attribute der GEO-JSON Struktur neu
        """
        elem = self.geo_info[hofladen['id']]['geo_elem_pos']
        geo_elem = self.geo_struct['features'][elem]
        for k in hofladen:
            if k == 'id':
                continue
            geo_elem['properties'][k] = hofladen[k]

    def save_geo_json(self):
        """
            Speicher die GEOJSON Strucktur
        """
        fname = "%s.new" % self.geo_json
        with open(fname, 'w') as fd:
            geojson.dump(self.geo_struct, fd)

    def init_hoflaeden(self):
        """
            initialiesiere die HofLaeden Tabelle neu
        """
        hof_id = 0
        first = True
        second = False
        hof_id = 0
        with open(self.csv_name, newline='') as csvfile:
            for laden in reader(csvfile, delimiter=',', quotechar='"'):
                if self.verbose > 1:
                    print("Hofladen: ", laden)
                if len(laden[LADENPOS]) == 0:
                    # leere Zeile am Anfang
                    continue
                if first:
                    self.__init_rubriken__(first=True, laden=laden)
                    first = False
                    second = True
                if second:
                    self.__init_rubriken__(second=True, laden=laden)
                    second = False
                    continue
                # Das sind die Läden
                hof_id += 1
                hofladen = {
                    'id' : hof_id,
                    'name' : laden[LADENPOS],
                    'kategorie' : laden[self.column['Kategorie']],
                    'adresse' : laden[self.column['Straße']],
                    'plz' : laden[self.column['PLZ']],
                    'ort' : laden[self.column['Ort']],
                    'tel_nr' : laden[self.column['Telefonnummer']],
                    'www' : laden[self.column['Homepage']],
                    'email' : laden[self.column['Email']],
                    'vertrieb' : laden[self.column['sonstiger Vertrieb']],
                    }
                if self.verbose:
                    print("Hofladen: %s" % pformat(hofladen))

                # Check ob bereits eine Koordinate existiert
                if hof_id not in self.geo_info:
                    # Hol die Geo Info mit OSM
                    print("Hole die Geo Information für den neuen Hof: '%s'"% (
                        hofladen['name']))
                    self.create_new_geo_json_elem(hofladen)
                    self.save_geo_json()
                # setz die 'Properties' NEU
                self.update_geo_json_elem(hofladen)

                # Check ob der Hof schon in der DB existiert
                try:
                    pg_laden = Hofladen.objects.get(id=hof_id)
                except:
                    self.create_new_postgres_entry(hof_id, hofladen)
                    continue
                self.update_pg_element(pg_laden, hofladen)

    def get_geo_coordinate(self, hofladen):
        """
            Hole von OSM die Koordinaten des Hofs
        """
        print("Hole die Geo Information für den neuen Hof: '%s'"% (
                        hofladen['name']))
        geo_pos = geocoder.osm("%s, %s %s" % (hofladen['adresse'], hofladen['plz'],
            hofladen['ort']))
        return [geo_pos.osm['x'], geo_pos.osm['y']]

    def update_pg_element(self, pg_laden, laden):
        """
            Setze die Attribute in der DB neu 
        """
        pg_laden.coordinate = self.geo_info[laden['id']]['coordinate']
        pg_laden.save()
        
    def create_new_postgres_entry(self, hof_id, laden):
        """
            Wenn der Laden noch nicht existiert generier ein neues DB
            Element
        """
        obj = Hofladen(id=hof_id,
            name=laden['name'],
            kategorie = laden['kategorie'],
            adresse=laden['adresse'],
            plz=laden['plz'],
            ort=laden['ort'],
            tel_nr=laden['tel_nr'],
            www=laden['www'],
            email=laden['email'],
            vertrieb=laden['vertrieb'],
            coordinate = self.geo_info[hof_id]['coordinate']
            )
        obj.save()


    def get_geo_objects(self, geo_json):
        """
            generier aus den Postgres Daten ein neues GEO-JSON Dict
        """
        if not geo_json or not exists(geo_json):
            print("Can't find geo_json file: '%s'" % geo_json)
            return {}

        with open(geo_json) as fd:
            self.geo_struct = geojson.load(fd)
        if self.verbose:
            print("get_geo_objects: %s" % pformat(self.geo_struct))
        return self.geo_struct

if __name__ == '__main__':

    hofl = hofladen('hofverkauf/Hofverkauf.csv',
                   'hofverkauf/hofladen.geojson',
                    verbose = 1,
                    TEST=True)

    hofl.init_hoflaeden()

    hofl.save_geo_json()
