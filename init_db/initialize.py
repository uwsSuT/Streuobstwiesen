#!/bin/python3


#
# Initialisiere die Obstsorten und Hoflaeden in der Postgres DB
#
# Damit wir das Django Models Modul verwenden können, muss zunächst die
# Django Umgebung gesetzt werden. Dass passiert durch die beiden Aufrufe
#
#   - settings.configure
#   - django.setup()
#
# Erst danach können die Models importiert werden !!!
#
#
# Hard coded Switch damit das Script auf Heroku laufen kann
#  Start auf Heroku
#   - heroku run bash -a hilgi-docker
#   - python ./init_db/initialize.py
#

import os
from os.path import exists
import django
from django.conf import settings
from pprint import pformat

from schtob.lib.util import compile_start_time
from baeume.baeume import BaumLeaflet
from init_db import Baeume_geo

from init_db.db_env import DATABASES

#
# Hard coded Switch damit das Script auf Heroku laufen kann
#  Start auf Heroku
#   - heroku run bash -a hilgi-docker
#   - python ./init_db/initialize.py
#
if not os.environ.get('HOSTNAME') == 'ubuntu18-srv':
    import dj_database_url
    db_from_env = dj_database_url.config()
    DATABASES['default'].update(db_from_env)
    DATABASES['default']['CONN_MAX_AGE'] = 500

if not settings.configured:
    settings.configure(
            DATABASES = DATABASES,
            INSTALLED_APPS = ['obstsorten'],
        )
    django.setup()


from csv import reader
from obstsorten.models import ObstSorten, Wiese, ObstBaum, ObstTypen
from obstsorten.defs import Obst_Type
#from hofladen.models import Hofladen

enums = {
        'obst_typen' : Obst_Type,
        }

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
                    # trag den Type extra ein
                    oname = 'unbekannt'
                    ot = Obst_Type.index(oname)
                    type_obj = ObstTypen.objects.get(name=oname)
                    obj = ObstSorten(sorten_id=999, obst_type=ot,
                            obst_sorte=oname, type_name=type_obj)
                    obj.save()
                    continue
                if obst_type == 'Tod':
                    # trag den Type extra ein
                    oname = 'Tod'
                    ot = Obst_Type.index(oname)
                    type_obj = ObstTypen.objects.get(name=oname)
                    obj = ObstSorten(sorten_id=1000, obst_type=ot,
                            obst_sorte=oname, type_name=type_obj)
                    obj.save()
                    continue
                try:
                    ot = Obst_Type.index(obst_type)
                    oname = obst_type
                    print("ot: %s oname: %s" % (ot, oname))
                except:
                    print("Unbekannter Obst-Type: %s" % obst_type)
                    ot = Obst_Type.index('unbekannt')
                    continue
                type_obj = ObstTypen.objects.get(name=oname)
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
                       alergie_info=alergie_info, www=www,
                       type_name=type_obj)
            obj.save()

def insert_wiesen(fname):
    """
        Initialisiere die Obstwiesen
    """
    with open(fname, newline='') as csvfile:
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

            obj = Wiese(wiesen_id=wiesen_id, name=name, obstwiese=obstwiese,
                    bluehwiese=bluehwiese, www_name=www_name)
            obj.save()

def insert_obsttypen():
    for ot in Obst_Type:
        obj = ObstTypen(name=ot)
        obj.save()

def re_init():
    delete_all()
    insert_obsttypen()
    insert_obstsorten('init_db/Obstsorten.csv')
    insert_wiesen('init_db/wiesen.txt')
    insert_baeume('init_db/Baeume.csv')

def delete_all():
    delete_obst_types()
    delete_baeume()
    delete_wiesen()
    delete_obstsorten()

def delete_obst_types():
    """
        Lösche alle Obstsorten für einen reinit
    """
    try:
        for sorte in ObstTypen.objects.all():
            sorte.delete()
    except:
        pass

def delete_obstsorten():
    """
        Lösche alle Obstsorten für einen reinit
    """
    try:
        for sorte in ObstSorten.objects.all():
            sorte.delete()
    except:
        print("ERROR: delete_obstsorten")
        pass

def delete_wiesen():
    """
        Lösche alle Wiesen für einen reinit
    """
    try:
        for wiese in Wiese.objects.all():
            wiese.delete()
    except:
        pass

def delete_baeume():
    """
        Lösche alle Bäume für einen reinit
    """
    try:
        for baum in ObstBaum.objects.all():
            baum.delete()
    except:
        pass

def insert_baeume(fname):
    BaumLeaflet(Baeume_geo, verbose=2)

if __name__ == '__main__':


    insert_obstsorten('init_db/Obstsorten.csv')
    insert_wiesen('init_db/wiesen.txt')
    insert_baeume('init_db/Baeume.csv')
