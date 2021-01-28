#!/bin/python3

import sys
from os.path import exists
import geocoder
import geojson
from csv import reader
from pprint import pformat

from hofladen.models import Hofladen, HofRubrik, Unterrubrik

LADENPOS = 1

class HofladenCl():
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
        self.rubrik_info = {}
        self.unterRubrik_info = {}
        self.pos2Rubrik = {}
        self.pos2unterRubrik = {}   ## welche Unterrubrik befindet sich an Position: X

        self.geo_info = {}

        if geo_json:
            self.__init_geo_json__()

        self.BioID = HofRubrik.objects.filter(name='Bio')[0].id
        self.SiegelID = HofRubrik.objects.filter(name='Siegel')[0].id

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

    def __check_rubrik_in_db__(self, rubrik):
        """
            Check ob die Rubrik bereits in der  DB enthalten ist wenn nicht
            füge sie hinzu.
            In beiden Fällen wird die DB-ID in dem lokalen Rubriken_Dict hinzugefügt
        """
        rub = HofRubrik.objects.filter(name=rubrik)
        if not rub:
            print("Add Rubrik 2 DB")
            obj = HofRubrik(
                name=rubrik)
            obj.save()
        else:
            obj = rub[0]
        print("Rubrik: %s" % pformat(obj))
        self.rubriken[self.rubrik_info[rubrik]['pos']]['id'] = obj

    def __check_unterrubrik__(self, urubrik, rubrik):
        """
            Check das es die Unterrubrik für die Rubrik bereits gibt
            Wenn Nein füge hinzu
            Auf auf alle Fälle füge die ID der Unetrrubrik in das Dict
        """
        new = False
        urub = Unterrubrik.objects.filter(name=urubrik, rubrik=rubrik)
        if not urub:
            print("Add UnterRubrik 2 DB: %s" % urubrik)
            obj = Unterrubrik(
                    name=urubrik,
                    rubrik=rubrik)
            obj.save()
            new = True
        else:
            obj = urub[0]
        print("UnterRubrik: %s" % pformat(obj))
        self.unterRubrik_info[urubrik] = { 'id' : obj }

        if new:
            #
            # Check ob die UnterRubrik auch in der Rubrik referenziert ist
            #
            if not rubrik.unter_rubriken:
                rubrik.unter_rubriken = [obj.id]
            elif obj.id not in rubrik.unter_rubriken:
                print("ADD UnterRubrik 2 Rubrik: %s:%s" % (urubrik, rubrik.name))
                rubrik.unter_rubriken.append(obj.id)
            rubrik.save()


    def __init_rubriken__(self, first=False, second=False, line=[]):
        """
            Initialisiere die Rubriken aus der ersten Zeilen des
            SpreadSheets
        """
        if first and line[LADENPOS] == 'Name':
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
            for p in range(len(line)):
                if line[p].upper() == 'BIO' or bio_found:
                    bio_found = True
                    if not line[p]:
                        continue
                    self.rubriken.append(
                        { 'name' : line[p],
                          'pos'  : p,
                          'unterrubrik' : [],
                          'id'   : 0,           # Reference zur PostgresDB
                        } )

                self.column[line[p]] = p        # Setz eine Liste aus der die Position im Spreadsheet
                                                # abgerufen werden kann
                self.pos2Rubrik[p] = line[p]
                self.rubrik_info[line[p]] = { 'pos' : len(self.rubriken)-1}
            #
            # Gleiche die Rubriken mit der DB ab
            #
            for rubrik in self.rubriken:
                self.__check_rubrik_in_db__(rubrik['name'])

        if second:
            # behandle die UnterRubriken
            print("rubriken: %s" % pformat(self.rubriken))
            print("column: %s" % pformat(self.column))
            rubrik = 0
            act_rubrik = 0
            for p in range(len(line)):
                if rubrik < len(self.rubriken) and \
                   p == self.rubriken[rubrik]['pos']:
                    act_rubrik = rubrik
                    rubrik += 1
                if line[p]:
                    self.rubriken[act_rubrik]['unterrubrik'].append(line[p])
                    self.__check_unterrubrik__(line[p], self.rubriken[act_rubrik]['id'])
                    self.pos2unterRubrik[p] = line[p]

            print("rubriken: %s" % pformat(self.rubriken))

    def __add_hof2Rubrik__(self, hof_id, rubrik):
        """
            Füge den Hof zu zur Rubrik hinzu
        """
        if self.verbose > 1:
            print("__add_hof2Rubrik__: hof_id: %s rubrik: %s name: %s laden_liste: %s" % (
                hof_id, rubrik, self.rubriken[rubrik]['name'],
                self.rubriken[rubrik]['id'].hofladen_list))
        if not self.rubriken[rubrik]['id'].hofladen_list:
            self.rubriken[rubrik]['id'].hofladen_list = [hof_id]
            self.rubriken[rubrik]['id'].save()
        elif hof_id not in self.rubriken[rubrik]['id'].hofladen_list:
            self.rubriken[rubrik]['id'].hofladen_list.append(hof_id)
            self.rubriken[rubrik]['id'].save()


    def __check_hof2Rubrik__(self, hof_id, values):
        """
            Gleich die Einträge der Angebote / Rubriken mit der DB ab
        """
        start_pos = self.rubriken[self.rubrik_info['Bio']['pos']]['pos']

        rubrik = 0  # fang mit der ersten Rubrik an
        act_rubrik = 0

        for p in range(start_pos, len(values)):
            if rubrik < len(self.rubriken) and \
               p == self.rubriken[rubrik]['pos']:
                act_rubrik = rubrik
                rubrik += 1

            if self.verbose > 2:
                print("p: %s rubrik: %s act_rubrik: %s" % (p, rubrik, act_rubrik))
            if values[p].upper() == 'JA':
                if self.verbose > 2:
                    print("value: JA")

                # Füge den Hof zur Rubrik hinzu
                if p in self.pos2Rubrik:
                    if self.verbose > 2:
                        print("add_hof 1")
                    self.__add_hof2Rubrik__(hof_id, act_rubrik)

                # Füge den Hof zur UnterRubrik hinzu
                added = False
                if p in self.pos2unterRubrik:
                    urub = self.unterRubrik_info[self.pos2unterRubrik[p]]
                    if not urub['id'].hofladen_list:
                        urub['id'].hofladen_list = [hof_id]
                        added = True

                    elif hof_id not in urub['id'].hofladen_list:
                        urub['id'].hofladen_list.append(hof_id)
                        added = True
                if added:
                    urub['id'].save()
                    # Und jetzt Check das der Hof auch in die Rubrik kommt
                    if self.verbose > 2:
                        print("add Hof 2")
                    self.__add_hof2Rubrik__(hof_id, act_rubrik)

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
                if self.verbose > 2:
                    print("Hofladen: ", laden)
                if len(laden[LADENPOS]) == 0 and \
                    not second:
                    # leere Zeile am Anfang
                    continue
                if first:
                    self.__init_rubriken__(first=True, line=laden)
                    first = False
                    second = True
                    continue
                if second:
                    self.__init_rubriken__(second=True, line=laden)
                    second = False
                    continue
                # Das sind die Läden
                hof_id += 1
                hofladen = {
                    'id' : hof_id,
                    'name' : laden[LADENPOS],
                    'adresse' : laden[self.column['Straße']],
                    'plz' : laden[self.column['PLZ']],
                    'ort' : laden[self.column['Ort']],
                    'tel_nr' : laden[self.column['Telefonnummer']],
                    'www' : laden[self.column['Homepage']],
                    'email' : laden[self.column['Email']],
                    'vertrieb' : laden[self.column['sonstiger Vertrieb']],
                    }
                if self.verbose > 1:
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
                pg_laden = Hofladen.objects.filter(id=hof_id)
                if not pg_laden:
                    self.create_new_postgres_entry(hof_id, hofladen)
                    continue
                self.update_pg_element(pg_laden[0], hofladen)

                #
                # Und jetzt gleichen wir die Rubriken und UnterRubriken mit der DB ab
                #
                self.__check_hof2Rubrik__(hof_id, laden)

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
        pg_laden.name = laden['name']
        pg_laden.adresse = laden['adresse']
        pg_laden.plz = laden['plz']
        pg_laden.ort = laden['ort']
        pg_laden.tel_nr = laden['tel_nr']
        pg_laden.www = laden['www']
        pg_laden.email = laden['email']
        pg_laden.vertrieb = laden['vertrieb']
        pg_laden.save()

    def create_new_postgres_entry(self, hof_id, laden):
        """
            Wenn der Laden noch nicht existiert generier ein neues DB
            Element
        """
        obj = Hofladen(id=hof_id,
            name=laden['name'],
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

    def __init_goejson_struct__(self):
        """
            Bau die GEOjson Strucktur auf
        """
        self.geojson_dict = {
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": {
                    "name": "EPSG:4326"
                }
            },
            "features": []
        }

    def __add_geo_feature__(self, hof):
        """
            Füge die Daten eines Hofs als neues Feature hinzu
        """
        feature = {
            "type": "Feature",
            "properties": {
                "name"      : hof.name,
                "id"        : hof.id,
                "www"       : hof.www,
                "adresse"   : hof.adresse,
                "ort"       : hof.ort,
                "Telefon"   : hof.tel_nr,
            },
            "geometry": {
                "type": "Point",
                "coordinates": hof.coordinate.split(','),
            }
        }
        self.geojson_dict['features'].append(feature)


    def get_geo_objects(self, geo_json_file="", rubrik_id=0, urubrik_id=0, bio=False):
        """
            generier
                - aus den Postgres Daten
            oder
                - aus dem geojson File
            ein neues GEO-JSON Dict
        """
        if geo_json_file:
            if not exists(geo_json_file):
                print("Can't find geo_json file: '%s'" % geo_json_file)
                return {}

            with open(geo_json_file) as fd:
                self.geo_struct = geojson.load(fd)
            if self.verbose > 1:
                print("get_geo_objects: %s" % pformat(self.geo_struct))
            return self.geo_struct
        if bio:
            if urubrik_id:
                rubrik_id = self.SiegelID
            else:
                rubrik_id = self.BioID

        #
        # lies die Daten aus der DB
        #
        self.__init_goejson_struct__()
        if urubrik_id:
            # Hol nur die Laeden die diese UnterRubrik (Artikel) haben
            urubrik = Unterrubrik.objects.get(id=urubrik_id)
            for hof_id in urubrik.hofladen_list:
                hof = Hofladen.objects.get(id=hof_id)
                self.__add_geo_feature__(hof)
        elif rubrik_id:
            # Hol nur die Laeden die diese Rubrik haben
            rubrik = HofRubrik.objects.get(id=rubrik_id)
            for hof_id in rubrik.hofladen_list:
                hof = Hofladen.objects.get(id=hof_id)
                self.__add_geo_feature__(hof)
        else:
            for hof in Hofladen.objects.all():
                self.__add_geo_feature__(hof)
        if self.verbose > 1:
            print("get_geo_objects: %s" % pformat(self.geojson_dict))
        return self.geojson_dict

    def get_rubriken(self):
        """
            Hol die Rubriken aus der PG-DB
        """
        rubriken = []
        for rub in HofRubrik.objects.all().order_by('name'):
            #
            # Die Öko-Siegel und die Rubrik Bio wollen nicht in das Rubriken Menü
            #
            if rub.name.upper() == 'BIO' or \
               rub.name.upper() == 'SIEGEL':
                continue
            rubriken.append(rub)
        return rubriken

    def get_unterrubriken(self):
        """
            Hol die Rubriken mit Ihren UnterRubriken für das Menu
        """
        unterrubrik = []
        for rubrik in HofRubrik.objects.all().order_by('name'):
            if rubrik.name.upper() == 'SIEGEL':
                continue
            d = {
                'name' : rubrik.name,
                'id' : rubrik.id,
                'unterrubrik' : [],
            }
            has_urubriks = False
            for urub in Unterrubrik.objects.filter(rubrik_id=rubrik.id):
                d['unterrubrik'].append({'name': urub.name, 'id' : urub.id})
                has_urubriks = True
            if has_urubriks:
                unterrubrik.append(d)
        if self.verbose > 1:
            print("get_unterrubriken: %s" % pformat(unterrubrik))
        return unterrubrik

    def get_oeko_siegel(self):
        """
            Hol die Namen (UnetrRubriken) der ÖkoSiegel
                Die stecken in der DB wie normale Rubriken und UnetrRubriken
        """
        siegel_list = []
        for siegel in Unterrubrik.objects.filter(rubrik_id=self.SiegelID):
            siegel_list.append(siegel)
        return siegel_list

if __name__ == '__main__':

    hofl = HofladenCl(csv_name='hofverkauf/Hofverkauf.csv',
                    geo_json='hofverkauf/hofladen.geojson',
                    verbose = 1,
                    TEST=True)

    hofl.init_hoflaeden()

    hofl.save_geo_json()
