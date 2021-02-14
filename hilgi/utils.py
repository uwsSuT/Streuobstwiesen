import os
from os.path import join, exists, isdir

DEBUG = int(os.environ.get('DEBUG', default=0))

"""
    Helper Classen für die Darstellung von Bäumen, Wiesen und
    Hofläden
"""
class GeoJsonClass():
    """
        Basis-Class für die Verwendung als LEAFLET Object
    """
    QueryArgs = ('baueme_statisch')

    def __init__(self):
        """
            Helper Class für die Darstellung von Bäumen und Hofläden
        """
        self.geojson_dict = self.__init_feature__()

    def __init_feature__(self):
        """
            gib einen GEO-JSOn Feature Strucktur zurück
        """
        return  {
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": {
                    "name": "EPSG:4326"
                }
            },
            "features": []
        }

    def init_layer(self, layer_names):
        """
            Bau einen GEOjson Strucktur für einen Layer auf
        """
        self.geo_layers = {}
        for name in layer_names:
            self.geo_layers[name] = self.__init_feature__()

class BaumPics():
    """
        Helper Class für die Verwlatung der BaumBilder
    """
    def __init__(self):
        self.baum_pics = {}
        pwd = os.getcwd()
        self.baum_dir = join(pwd, 'static', 'images', 'baum')

    def init_baum_pic(self, baum):
        """
            such die zur baum_id zugehörigen Bilder in dem Static Verzeichnis
            gib diese als Liste zurück
        """
        wiesen_name = baum.wiese.name
        if not exists(self.baum_dir):
            if DEBUG:
                print("Could not find: %s" % self.baum_dir)

        for f in os.listdir(self.baum_dir):
            if isdir(join(self.baum_dir, f)) and \
                    f == wiesen_name:
                if DEBUG:
                    print("FOUND Dir: %s" % f)
                for b in os.listdir(join(self.baum_dir, f)):
                    if b.find("%s_" % baum.baum_id) == 0:
                        if DEBUG:
                            print("FOUND Tree: %s" % b)
                        if not baum.baum_id in self.baum_pics:
                            self.baum_pics[baum.baum_id] = []
                        self.baum_pics[baum.baum_id].append(
                                    join('/', 'static', 'images', 'baum', f, b))

    def get_all_pics(self, baum):
        return self.baum_pics[baum.baum_id]

    def get_first_pic(self, baum):
        return sorted(self.baum_pics[baum.baum_id])[0]

class BaumSessionClass():
    # Umschalten der Wiesen/ Baum-Anzeige
    # wird über ein Ansichts-Menu geschaltet und im view.py ausgewertet
    # und im base.html verwendet
    def __init__(self):
        self.baeume_dynamisch = ""
        self.baeume_statisch = "disabled"

    def set_query2session(self, request, valname, value):
        """
             setz die aktuelle query in die Session/Cookie Umgebung für evtl.
             spätere Abfragen
        """
        request.session[valname] = value

    def get_query2session(self, request, valname):
        """
            Hol den Wert aus der Session Umgebung
        """
        if valname in request.session:
            return request.session[valname]
        elif valname == 'baeume_statisch':
            return self.baeume_statisch
        else:
            return self.baeume_dynamisch

