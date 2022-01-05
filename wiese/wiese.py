#!/bin/python3

import sys
import os
from os.path import exists, join
import geojson
import codecs
from pprint import pformat

from hilgi.utils import GeoJsonClass

DEBUG = int(os.environ.get('DEBUG', default=0))

class WiesenLeaflet(GeoJsonClass):
    """
            Class für die Generierung von GEO-Json Elementen
            zur Darstellung von Wiesen auf Polygon Basis
    """
    def __init__(self, geo_json_file="", verbose=0, TEST=False,
                 *args, **kwargs):
        super().__init__(*args, **kwargs) # Initialisiere die GeoJsonClass

        self.verbose = verbose
        self.TEST = TEST
        self.geo_json_file = geo_json_file

        if geo_json_file:
            if not exists(geo_json_file):
                print("ERROR: Konnte die GEO-Json Datei '%s' nicht finden" % (
                                geojson))
                sys.exit(1)
            self.__init_geo_json__()

    def __init_geo_json__(self):
        """
                lies das gegebene GEO-JSON File
        """
        with codecs.open(self.geo_json_file, 'r', 'utf-8') as fd:
            self.geo_struct = geojson.load(fd)

        if self.verbose:
            for geo_pos in self.geo_struct['features']:
                print("Wiese: %s" % pformat(geo_pos))

    def get_geo_objects(self,):
        return self.geo_struct

    def get_geo_info4wiese(self, wname):
        """
            Such die Wiese mit dem Namen und gib die Geo-Info zurück
        """
        for geo_pos in self.geo_struct['features']:
            if geo_pos['properties']['Ort'] == wname:
                return geo_pos
        return {}

class BluewiesenLeaflet(WiesenLeaflet):
    """
        Class für die Besonderheiten der Blühwiesen
    """
    def add_wiesen_pics(self):
        """
            Füge für jede Wiese ein Bild hinzu
        """
        pic_basename = join('static', 'images', 'bluehwiesen')
        pwd = os.getcwd()
        wdir = join(pwd, pic_basename)
        for geo_pos in self.geo_struct['features']:
            picture = { 
                    'name'  : '',
                    'datum' : 0,
                }
            for f in os.listdir(wdir):
                wname = geo_pos['properties']['Name'].replace(' ', '_')
                if wname == f:
                    for p in os.listdir(join(wdir, f)):
                        pstat = os.stat(join(wdir, f, p))
                        if pstat.st_mtime > picture['datum']:
                            picture['name'] = join('/', pic_basename, f, p)
                            picture['datum'] = pstat.st_mtime
            geo_pos['properties']['wpic'] = picture['name']
            geo_pos['properties']['wname'] = wname
            if self.verbose:
                print("BluewiesenPicture: %s" % geo_pos['properties'])

    def get_wiesen_infos(self):
        """
            Hol aus der GeoJson Datei die Infos (Name, Zeitpunkte, ...)
            und alle zugehörigen Bilder
        """
        pic_basename = join('static', 'images', 'bluehwiesen')
        pwd = os.getcwd()
        wdir = join(pwd, pic_basename)
        self.wiesen_infos = {}
        for geo_pos in self.geo_struct['features']:
            wid = geo_pos['properties']['id']
            self.wiesen_infos[wid] = geo_pos['properties']
            self.wiesen_infos[wid]['pictures'] = []

            nr = 0  # wird für das Karussel im HTML gebraucht
            for f in os.listdir(wdir):
                wname = geo_pos['properties']['Name'].replace(' ', '_')
                if wname == f:
                    for p in os.listdir(join(wdir, f)):
                        self.wiesen_infos[wid]['pictures'].append(
                            { 'nr' : nr,
                              'pic' : join('images', 'bluehwiesen', f, p),
                            })
                        nr += 1

        if self.verbose:
            print("get_wiesen_infos: %s" % pformat(self.wiesen_infos))
        print("get_wiesen_infos: %s" % pformat(self.wiesen_infos))

if __name__ == '__main__':
    #
    # Nur für Test-Zwecke
    #
    WiesenLeaflet(geo_json_file="init_db/Streuobstwiesen.geojson",
            verbose=2, TEST=True)
