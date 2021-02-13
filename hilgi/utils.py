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

