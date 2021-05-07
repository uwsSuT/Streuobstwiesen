
from os.path import exists
import geojson
import codecs
from csv import reader
from pprint import pformat

from obstsorten.defs import Obst_Type

class Wiesen():
    def __init__(self, wiesen_csv=''):
        """
            Lies ein CSV File ein und generiere ein Wiesen-Dict
        """
        if not exists(wiesen_csv):
            self.err = "ERROR: Wiesen-File '%s' existiert nicht" % wiesen_csv
            print(self.err)
            return

        self.wiesen = {}
        self.wiesen_names = {}
        with open(wiesen_csv, newline='') as csvfile:
            for l in csvfile:
                # Kommentar
                if l.strip()[0] == '#':
                    continue
                if len(l.strip()) == 0:
                    continue
                vals = l.split(':')
                wiesen_id = int(vals[0])
                name      = vals[1]
                obstwiese = vals[2].upper() == 'TRUE'
                bluehwiese = vals[3].upper() == 'TRUE'
                www_name  = vals[4].strip()

                self.wiesen[wiesen_id] = {
                    'name'       : name,
                    'obstwiese'  : obstwiese,
                    'bluehwiese' : bluehwiese,
                    'www_name'   : www_name,
                    'nr'         : wiesen_id,
                    }
                self.wiesen_names[name] = {
                    'name'       : name,
                    'obstwiese'  : obstwiese,
                    'bluehwiese' : bluehwiese,
                    'www_name'   : www_name,
                    'nr'         : wiesen_id,
                    }

class BaumInfos():
    def __init__(self, geo_json_file='', verbose=0):
        """
            Lies ein GeoJson Baum File
        """
        self.verbose = verbose
        if not exists(geo_json_file):
            self.err = "ERROR: GEO-Json-File '%s' existiert nicht" % geojson
            print(self.err)
            return

        with codecs.open(geo_json_file, 'r', 'utf-8') as fd:
            self.geo_struct = geojson.load(fd)

        self.baum_infos = {}
        self.wiesen_infos = {}
        for geo_pos in self.geo_struct['features']:
            if self.verbose:
                print("Baum: %s" % pformat(geo_pos))

            self.baum_infos[geo_pos['properties']['Baum_Nr']] = geo_pos['properties']
            if not geo_pos['properties']['Wiesen_Nr'] in self.wiesen_infos:
                self.wiesen_infos[geo_pos['properties']['Wiesen_Nr']] = []
            self.wiesen_infos[geo_pos['properties']['Wiesen_Nr']].append(geo_pos['properties']['Baum_Nr'])

class ObstInfos():
    def __init__(self, obst_csv='', verbose=0):
        """
            Lies die Obstsorten Infos aus einem CSV File ein
        """
        self.csv_file = obst_csv
        self.verbose = verbose

        if not exists(obst_csv):
            self.err = "ERROR: ObstsortenFile '%s' existiert nicht" % obst_csv
            print(self.err)
            return

        self.obstsorten = {}
        self.read_csv()

    def read_csv(self):
        first = True
        with open(self.csv_file, newline='') as csvfile:
            for frucht in reader(csvfile, delimiter=',', quotechar='"'):
                if first:
                    # Überschriften
                    first = False
                    continue
                if self.verbose:
                    print("frucht: ", frucht)
                if 'SUMME' in frucht[0].upper():
                    continue
                elif frucht[0]:
                    # neuer Obsttype
                    obst_type = frucht[0].strip()
                    if obst_type == 'unbekannter Baum':
                        # trag den Type extra ein
                        ot = Obst_Type.index('unbekannt')
                        continue
                    if obst_type == 'Tod':
                        # trag den Type extra ein
                        ot = Obst_Type.index('Tod')
                        continue
                    try:
                        ot = Obst_Type.index(obst_type)
                    except:
                        print("Unbekannter Obst-Type: %s" % obst_type)
                        ot = Obst_Type.index('unbekannt')
                    continue
                elif not frucht[0] and not frucht[1]:
                    # Leere Zeile
                    continue
                else:
                    sid = int(frucht[1].strip())
                    self.obstsorten[sid] = {
                        'sid'             : sid,
                        'obst_sorte'      : frucht[2].strip(),
                        'obst_type'       : obst_type,
                        'pflueck_reif'    : frucht[5].strip(),
                        'genuss_reif'     : frucht[5].strip(),
                        'verwendung'      : frucht[6].strip(),
                        'geschmack'       : frucht[7].strip(),
                        'lagerfaehigkeit' : frucht[8].strip(),
                        'alergie_info'    : frucht[9].strip(),
                        'www'             : frucht[11].split(),
                        }
