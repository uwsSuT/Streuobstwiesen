#!/bin/python3

#
# Initialisiere die Obstsorten in der Postgres DB
#

from csv import reader
from obstsorten.models import ObstSorten, Obst_Type

def insert_obstsorten(fname):
    """
        fname ist eine CSV Datei in der die Obstsorten mit Ihren 
        Attributen definiert sind
    """
    first = True
    with open(fname, newline='') as csvfile:
        for frucht in reader(csvfile, delimiter=',', quotechar='"'):
            if first:
                # Überschriften
                first = False
                continue
            print("frucht: ", frucht)
            if 'SUMME' in frucht[0].upper():
                continue
            elif frucht[0]:
                # neuer Obsttype
                obst_type = frucht[0].strip()
                if obst_type == 'unbekannter Baum':
                    # targ den Type extra ein
                    ot = Obst_Type.index('unbekannt')
                    obj = ObstSorten(sorten_id=999, obst_type=ot,
                            obst_sorte='unbekannt')
                    obj.save()
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
                obst_sorte = frucht[2].strip()
                pflueck_reif = frucht[5].strip()
                genuss_reif = frucht[5].strip()
                verwendung = frucht[6].strip()
                geschmack = frucht[7].strip()
                lagerfaehigkeit = frucht[8].strip()
                alergie_info = frucht[9].strip()
                www = frucht[11].split()

            obj = ObstSorten(sorten_id=sid, obst_type=ot, obst_sorte=obst_sorte,
                       pflueck_reif=pflueck_reif, genuss_reif=genuss_reif,
                       verwendung=verwendung, geschmack=geschmack,
                       lagerfaehigkeit=lagerfaehigkeit,
                       alergie_info=alergie_info, www=www)
            obj.save()


if __name__ == '__main__':

    insert_obstsorten('Obstsorten.csv')
