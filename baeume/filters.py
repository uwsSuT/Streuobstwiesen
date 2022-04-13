from pprint import pformat
from django_filters import CharFilter, DateFilter, FilterSet, DateTimeFilter, ChoiceFilter, BooleanFilter

from obstsorten.models import ObstBaum, ObstSorten
from obstsorten.utils import get_sorten_names, get_sorten_typ, get_wiesen_names

class BaumInfosFilter(FilterSet):
    duengung_choice = (
        ('', 'Düngung'),
        ('True', 'nötig'),
        ('False', 'nicht nötig'),
    )

    baum_nr = CharFilter(field_name='baum_id')
    obst_typ = ChoiceFilter(field_name='sorten_id__type_name__id',
                choices=get_sorten_typ(gen_tuple=True), 
                lookup_expr='icontains', empty_label=None)
    obst_sorte = ChoiceFilter(field_name='sorten_id__sorten_id',
                choices=get_sorten_names(gen_tuple=True), empty_label=None)
    wiese = ChoiceFilter(field_name='wiese__wiesen_id',
                choices=get_wiesen_names(gen_tuple=True), empty_label=None)
    zustand = CharFilter(field_name='zustand', lookup_expr='icontains')
    duengung_noetig = ChoiceFilter(field_name='duengung_noetig',
               choices=duengung_choice, empty_label=None)

