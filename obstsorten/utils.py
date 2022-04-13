from obstsorten.models import ObstSorten, Wiese, ObstTypen

def get_sorten_names(gen_tuple=False):
    """
    Die Funktion gibt für den ObstBaum Filter die Namen der bekannten 
    Obstsorten zurück
    """

    if gen_tuple:
        t = (('', 'Alle Obstsorten'),)
    else:
        t = []

    # MAKEMIGRATIONS_ERROR - START
    for sorte in ObstSorten.objects.all().order_by('obst_sorte'):
        if gen_tuple:
            t += ((sorte.sorten_id, sorte.obst_sorte), )
        else:
            t.append(("%s" % sorte.sorten_id, sorte.obst_sorte))
    # MAKEMIGRATIONS_ERROR - END
    return t

def get_sorten_typ(gen_tuple=False):
    """
    Die Funktion gibt für den ObstBaum Filter die Namen der bekannten 
    Obst-Typen zurück
    """

    if gen_tuple:
        t = (('', 'Alle Obsttypen'),)
    else:
        t = []

    otypes = []
    # MAKEMIGRATIONS_ERROR2 - START
    for otyp in ObstTypen.objects.all().order_by('name'):
        if gen_tuple:
            t += ((otyp.id, otyp.name), )
        else:
            t.append(("%s" % otyp.id, otyp.name))
    # MAKEMIGRATIONS_ERROR2 - END
    return t

def get_wiesen_names(gen_tuple=False):
    """
    Die Funktion gibt für den ObstBaum Filter die Namen der bekannten 
    Wiesen zurück
    """

    if gen_tuple:
        t = (('', 'Alle Wiesen'),)
    else:
        t = []

    # MAKEMIGRATIONS_ERROR3 - START
    for wiese in Wiese.objects.all().order_by('name'):
        if gen_tuple:
            t += ((wiese.wiesen_id, wiese.www_name), )
        else:
            t.append(("%s" % wiese.wiesen_id, wiese.www_name))
    # MAKEMIGRATIONS_ERROR3 - END
    return t
