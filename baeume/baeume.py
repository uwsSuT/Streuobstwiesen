#!/bin/python3

import sys
from os.path import exists
import geojson
import codecs
from csv import reader
from pprint import pformat

from obstsorten.models import ObstBaum, ObstSorten, Obst_Type
from wiese.models import Wiese
from schtob.lib.util import compile_start_time
from hilgi.utils import GeoJsonClass, BaumPics

class BaumLeaflet(GeoJsonClass, BaumPics):
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
        BaumPics.__init__(self, *args, **kwargs) # Initialisiere die BaumPicClass

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

    def __add_geo_feature__(self, baum, layer=None):
        """
            Füge die Daten eines Baums als neues Feature hinzu
        """
        #obst_sorte = ObstSorten.objects.get(sorten_id=baum.sorten_id)
        self.init_baum_pic(baum)
        # baum_pic = self.get_first_pic(baum)
        try:
            feature = {
                "type": "Feature",
                "properties": {
                    "baum_nr"   : baum.baum_id,
                    "sorte"     : baum.sorten_id.obst_sorte,
                    'obst_type' : Obst_Type[baum.sorten_id.obst_type],
                    'baum_pic'  : self.get_first_pic(baum),
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": baum.coordinate.split(','),
                }
            }
        except:
            print("ERROR at:__add_geo_feature__: baum: %s" % pformat(baum))
            return
        if layer:
            layer['features'].append(feature)
        else:
            self.geojson_dict['features'].append(feature)

    def get_all_geo_objects(self,):
        """
            hole die Bäume aus der DB und füge sie in
            das geo_josn_dict
        """
        for baum in ObstBaum.objects.all():
            self.__add_geo_feature__(baum)
        return self.geojson_dict

    def get_geo_objects4sorte(self, sorten_id):
        """
            hole alle Bäume der Sorte in gib sie in einem geojson dict zurück
        """
        for baum in ObstBaum.objects.filter(sorten_id=sorten_id):
            print("get_geo_objects4sorte: %s" % pformat(baum))
            self.__add_geo_feature__(baum)
        print("get_geo_objects4sorte: %s" % pformat(self.geojson_dict))
        return self.geojson_dict

    def get_all_trees4wiese(self, wid):
        """
            Hole alle Bäume für die Wiese und pack sie in Obst-Sorten Layer
        """
        sorten_layer = {}
        self.init_layer(Obst_Type)
        for osorte in ObstSorten.objects.all():
            for baum in ObstBaum.objects.filter(wiese_id=wid, sorten_id=osorte.sorten_id):
                # print("get_all_trees4wiese: %s" % pformat(baum))
                # füg den Baum in den zugehörigen ObstType ein
                self.__add_geo_feature__(baum,
                                         layer=self.geo_layers[Obst_Type[osorte.obst_type]])
        # print("get_all_trees4wiese: Layers: %s" % pformat(self.geo_layers))
        return self.geo_layers

if __name__ == '__main__':

    BaumLeaflet(geo_json_file='init_db/Baeume.geojson',
            verbose=2, TEST=True)
