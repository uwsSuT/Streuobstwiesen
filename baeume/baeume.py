#!/bin/python3

import sys
from os.path import exists
import geojson
import codecs
from csv import reader
from pprint import pformat

from obstsorten.models import ObstBaum, ObstSorten, Wiese, Obst_Type
from schtob.lib.util import compile_start_time
from hilgi.utils import GeoJsonClass

class BaumLeaflet(GeoJsonClass):
    """
     Mamagement Class für das Lesen und Verwalten von GEO-Json Baum
     Elementen.
     Die Daten können entweder aus eine GEO-Json Datei oder aus
     einer Postgres-DB geladen werden.

     in der Funktion "get_geo_objects()" erhält man für "leaflet"
     geeignete Dict-Strucktur mit allen Bäumen.
        - letzteres funktioniert zurzeit aber nur auf Basis der DB
    """
    def __init__(self, geo_json_file="", verbose=0, TEST=False,
        *args, **kwargs):
        super().__init__(*args, **kwargs) # Initialisiere die GeoJsonClass

        self.verbose = verbose
        self.TEST = TEST
        self.geo_json_file = geo_json_file

        if geo_json_file:
            if not exists(geo_json_file):
                print("ERROR: Konnte die GEO-Jsom Datei '%s' nicht finden" % (
                                geojson))
                sys.exit(1)
            self.__init_geo_json__()


    def __init_geo_json__(self):
        """
                lies das gegebene GEO-JSON File
        """
        with codecs.open(self.geo_json_file, 'r', 'utf-8') as fd:
            self.geo_struct = geojson.load(fd)

        bid = 1
        for geo_pos in self.geo_struct['features']:
            if self.verbose:
                print("Baum: %s" % pformat(geo_pos))
            bid = geo_pos['properties']['Baum_Nr']
            sorten_id = ObstSorten.objects.get(
                            sorten_id=geo_pos['properties']['id'])
            wiese = Wiese.objects.get(
                            wiesen_id=geo_pos['properties']['Wiesen_Nr'])
            zustand = geo_pos['properties']['Zustand']
            if geo_pos['properties']['Schnitt']:
                    letzter_schnitt = compile_start_time(
                            geo_pos['properties']['Schnitt'],
                            tformat='DATETIME')
            else:
                letzter_schnitt = None
            try:
                coordinate = "%s, %s" % (
                    geo_pos['geometry']['coordinates'][0],
                    geo_pos['geometry']['coordinates'][1])
            except:
                print("Error for Baum ID: %s" % geo_pos['properties']['Baum_Nr'])
                continue

            if not zustand:
                zustand = ""
            try:
                baum = ObstBaum.objects.get(baum_id=bid)
            except:
                baum = 0 # den Baum gibt es noch nicht
#            if baum:
#                obj = ObstBaum(sorten_id=sorten_id, wiese=wiese,
#                           zustand=zustand, letzter_schnitt=letzter_schnitt)
#            else:
            obj = ObstBaum(baum_id=bid, sorten_id=sorten_id, wiese=wiese,
                           zustand=zustand, letzter_schnitt=letzter_schnitt,
                           coordinate=coordinate)
            obj.save()

    def __add_geo_feature__(self, baum):
        """
            Füge die Daten eines Baums als neues Feature hinzu
        """
        #obst_sorte = ObstSorten.objects.get(sorten_id=baum.sorten_id)
        try:
            feature = {
                "type": "Feature",
                "properties": {
                    "baum_nr"   : baum.baum_id,
                    "sorte"     : baum.sorten_id.obst_sorte,
                    'obst_type' : Obst_Type[baum.sorten_id.obst_type],
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": baum.coordinate.split(','),
                }
            }
        except:
            print("__add_geo_feature__: baum: %s" % pformat(baum))
            return
        self.geojson_dict['features'].append(feature)

    def get_geo_objects(self,):
        """
                hole die Bäume aus der DB und füge sie in
                das geo_josn_dict
        """
        for baum in ObstBaum.objects.all():
            self.__add_geo_feature__(baum)
        return self.geojson_dict

if __name__ == '__main__':

    BaumLeaflet(geo_json_file='init_db/Baeume.geojson',
            verbose=2, TEST=True)
