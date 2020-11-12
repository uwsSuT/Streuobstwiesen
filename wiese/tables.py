from django_tables2 import tables, TemplateColumn, CheckBoxColumn
from django_tables2.columns import DateTimeColumn, LinkColumn

from obstsorten.models import Wiese

class WiesenTable(tables.Table):

    class Meta:
        model = Wiese
        template_name = "django_tables2/bootstrap4.html"
        attrs = { 'class'   : 'table table-striped table-bordered table-hover',
                }
        row_attrs = {
                'data-id' : lambda record: record.pk,
                }
        fields = ('wiesen_id', 'name')

    # generiere einen URL-Link für den Namen-der Wiese
    wiesen_id =  TemplateColumn('<a href="/wiese/{{record.pk}}">{{record.wiesen_id}}</a>')
    name = TemplateColumn('<a href="/wiese/{{record.pk}}">{{record.name}}</a>')
