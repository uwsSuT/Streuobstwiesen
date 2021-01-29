from django_tables2 import tables, TemplateColumn

from .models import Hofladen

from pprint import pformat

class HofladenTable(tables.Table):

    class Meta:
        model = Hofladen
        template_name = "django_tables2/bootstrap4.html"

        attrs = { 'class': 'table table-striped table-bordered table-hover',
            }
        row_attrs = { 'data-id' : lambda record: record.id,
            }
        fields = ('name', 'adresse', 'plz', 'ort', 'tel_nr', 'www', 'email')
    
    # generier einen Link für die WWW-Seite
    www = TemplateColumn('<a href="{{record.www}}">{{record.www}}</a>')
    email = TemplateColumn('<a href="mailto:{{record.email}}">{{record.email}}')
    