from django_tables2 import tables, TemplateColumn, CheckBoxColumn
from django_tables2.columns import DateTimeColumn, LinkColumn

from obstsorten.models import ObstBaum

class WiesenTable(tables.Table):

    class Meta:
        model = ObstBaum
        template_name = "django_tables2/bootstrap4.html"
        attrs = { 'class'   : 'table table-striped table-bordered table-hove    r',
                }
        row_attrs = {
                'data-id' : lambda record: record.pk,
                }
        fields = ('baum_id', 'sorte', 'zustand', 'letzter_schnitt')

    sorte = TemplateColumn('<a href="/obstsorten_detail/{{record.pk}}">{{record.sorten_id.obst_sorte}}</a>')

