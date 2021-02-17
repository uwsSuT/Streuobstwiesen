#!/bin/python3

import sys
from os.path import exists
import geojson
import codecs
from pprint import pformat

from hilgi.utils import GeoJsonClass

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

if __name__ == '__main__':
    #
    # Nur für Test-Zwecke
    #
    WiesenLeaflet(geo_json_file="init_db/Streuobstwiesen.geojson",
            verbose=2, TEST=True)
