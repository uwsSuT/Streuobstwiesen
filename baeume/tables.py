import os
import re
from pprint import pformat

from django_tables2 import tables, TemplateColumn, CheckBoxColumn, Column
from django_tables2.columns import DateTimeColumn
from django_tables2.utils import A

from obstsorten.models import ObstBaum

from schtob.lib.dbg import dprint

DEBUG = int(os.environ.get('DEBUG', default=1))

class BaumInfosTable(tables.Table):

    class Meta:
        model = ObstBaum
        template_name = "django_tables2/bootstrap4.html"
        attrs = { 'class'   : 'table table-striped table-bordered table-hover',
                }
        row_attrs = {
                'data-id' : lambda record: record.pk,
                }
        fields = ('baum_id', 'sorten_id__type_name__name', 'wiese__name',
                  'zustand',
                  'letzter_schnitt', 'letzte_duengung', 'duengung_noetig')


