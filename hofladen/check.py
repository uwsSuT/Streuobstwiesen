#!/bin/python3

#
# Check die Informationen der Hoflaeden in der Postgres DB
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

import django
from django.conf import settings
from pprint import pformat

from schtob.lib.util import compile_start_time

from schtob.init_db.db_env import DATABASES

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
from obstsorten.models import Obst_Type, ObstSorten, ObstBaum
from wiese.models import Wiese
from hofladen.models import Hofladen

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
                    ot = Obst_Type.index('unbekannt')
                    obj = ObstSorten(sorten_id=999, obst_type=ot,
                            obst_sorte='unbekannt')
                    obj.save()
                    continue
                if obst_type == 'Tod':
                    # trag den Type extra ein
                    ot = Obst_Type.index('Tod')
                    obj = ObstSorten(sorten_id=1000, obst_type=ot,
                            obst_sorte='Tod')
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

def insert_wiesen(fname):
    """
        Initialisiere die Obstwiesen
    """
    with open(fname, newline='') as csvfile:
        for l in csvfile:
            vals = l.split(':')
            wiesen_id = int(vals[0])
            name      = vals[1]
            obstwiese = vals[2].upper() == 'TRUE'
            bluehwiese = vals[2].upper() == 'FALSE'

            obj = Wiese(wiesen_id=wiesen_id, name=name, obstwiese=obstwiese,
                    bluehwiese=bluehwiese)
            obj.save()


def re_init():
    delete_all()
    insert_obstsorten('init_db/Obstsorten.csv')
    insert_wiesen('init_db/wiesen.txt')
    insert_baeume('init_db/Baeume.csv')

def delete_all():
    delete_baeume()
    delete_wiesen()
    delete_obstsorten()

def delete_obstsorten():
    """
        Lösche alle Obstsorten für einen reinit
    """
    for sorte in ObstSorten.objects.all():
        sorte.delete()

def delete_wiesen():
    """
        Lösche alle Wiesen für einen reinit
    """
    for wiese in Wiese.objects.all():
        wiese.delete()

def delete_baeume():
    """
        Lösche alle Bäume für einen reinit
    """
    for baum in ObstBaum.objects.all():
        baum.delete()


def insert_baeume(fname):
    """
        Initialisiere die Baum-Tabelle

        Das BAUM-CSV File hat zurzeit noch sehr viele Spalten deren Inhalt
        zum Teil redundant ist, In der DB wollen wir aber nur eindeutige Daten
        ablegen
        Der Obst-Type ergibt sich aus der ID
              1 -  99 : Apfel
            101 - 199 : Birne
            201 - 299 : Zwetschge
            301 - 399 : Kirsche
            401 - 499 : Nuss
            501       : Mispel
            999       : unbekannt
            1000      : Der Baum ist Tod :-(

        Die Bäume haben zurzeit nur teilweise Nummern, daher zählen wir,
        die anderen selbst hoch
    """
    baum_id = 0
    first = True
    with open(fname, newline='') as csvfile:
        for baum in reader(csvfile, delimiter=',', quotechar='"'):
            print("Baum: ", baum)
            if first:
                # Überschriften
                first = False
                #
                # extrahiere aus den Überschriftnamen die Position für unten
                # Eine Änderung in der Atttributtabelle im GIS kann zu einer
                # Änderung der Reihenfolge führen
                #
                for i in range(len(baum)):
                    if baum[i] == 'id':
                        nr_id = i
                    elif baum[i].upper() == 'WIESEN_NR':
                        nr_wiese = i
                    elif baum[i].upper() == 'ZUSTAND':
                        nr_zustand = i
                    elif baum[i].upper() == 'SCHNITT':
                        nr_schnitt = i
                    elif baum[i].upper() == 'BAUM_NR':
                        nr_baum = i
                continue
            if not baum[nr_baum]:
                baum_id += 1
                bid = baum_id
            else:
                bid = int(baum[nr_baum])
            try:
                sorten_id = ObstSorten.objects.get(sorten_id=int(baum[nr_id]))
                wiese = Wiese.objects.get(wiesen_id=int(baum[nr_wiese]))
            except:
                print("COULD Not initialize Tree: %s" % pformat(baum))
                continue
            zustand = baum[nr_zustand]
            if baum[nr_schnitt]:
                letzter_schnitt = compile_start_time(baum[nr_schnitt],
                            tformat='DATETIME')
            else:
                letzter_schnitt = None

            obj = ObstBaum(baum_id=bid, sorten_id=sorten_id, wiese=wiese,
                           zustand=zustand, letzter_schnitt=letzter_schnitt)
            obj.save()

def init_hoflaeden(fname, TEST=False):
    """
        initialiesiere die HofLaeden Tabelle neu
    """
    hof_id = 0
    first = True
    second = False
    hof_id = 0
    with open(fname, newline='') as csvfile:
        for laden in reader(csvfile, delimiter=',', quotechar='"'):
            print("Hofladen: ", laden)
            if first:
                column = {}
                if len(laden[0]) == 0:
                    # leere Zeile am Anfang
                    continue
                if laden[0] == 'Name':
                    first = False
                    second = True
                    # Vanessas Spreadsheet hat unschöne Überschriften
                    # die in 2 Zeilen aufgeteilt sind
                    #   Bsp.
                    # Obst,,,,Bienenprodukte,,
                    # Beere,Apfel,Birne,....,Honig,Propolis
                    #
                    # D.h. aus der ersten Zeile müssen wir die Überschriften
                    # ermitteln und aus der Folgezeile die
                    #    Unterkategorie
                    rubriken = []
                    bio_found = False
                    for p in range(len(laden)):
                        if laden[p] == 'Bio' or bio_found:
                            bio_found = True
                            if not laden[p]:
                                continue
                            rubriken.append(
                                { 'name' : laden[p],
                                  'pos'  : p,
                                  'unterrubrik' : []
                                } )
                        else:
                            column[laden[p]] = p
                continue
            if second:
                second = False
                # behandle die Rubriken
                print("rubriken: %s" % pformat(rubriken))
                print("column: %s" % pformat(column))
                rubrik = 0
                for p in range(len(laden)):
                    if rubrik < len(rubriken) and \
                       p == rubriken[rubrik]['pos']:
                        act_rubrik = rubrik
                        rubrik += 1
                    if laden[p]:
                        rubriken[act_rubrik]['unterrubrik'].append(laden[p])
                print("rubriken: %s" % pformat(rubriken))
                continue
            # Das sind die Läden
            hof_id += 1
            if TEST:
                hofladen = {
                    'id' : hof_id,
                    'name' : laden[0],
                    'adresse' : laden[column['Straße']],
                    'plz' : laden[column['PLZ']],
                    'ort' : laden[column['Ort']],
                    'tel_nr' : laden[column['Telefonnummer']],
                    'www' : laden[column['Homepage']],
                    'email' : laden[column['Email']],
                    'vertrieb' : laden[column['sonstiger Vertrieb']],
                    }
                print("Hofladen: %s" % pformat(hofladen))
            else:
                obj = Hofladen(id=hof_id,
                    name=laden[0],
                    adresse=laden[column['Straße']],
                    plz=laden[column['PLZ']],
                    ort=laden[column['Ort']],
                    tel_nr=laden[column['Telefonnummer']],
                    www=laden[column['Homepage']],
                    email=laden[column['Email']],
                    vertrieb=laden[column['sonstiger Vertrieb']])
                obj.save()


if __name__ == '__main__':


    insert_obstsorten('init_db/Obstsorten.csv')
    insert_wiesen('init_db/wiesen.txt')
    insert_baeume('init_db/Baeume.csv')

    init_hoflaeden('hofverkauf/Hofverkauf.csv', TEST=True)
