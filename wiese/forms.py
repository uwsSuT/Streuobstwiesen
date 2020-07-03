from django import forms

from obstsorten.models import Wiese

class WieseModelForm(forms.ModelForm):
    class Meta:
        model = Wiese
        fields = [
            'wiesen_id',
            'name',
            'obstwiese',
            'bluehwiese',
        ]

class WiesenUpdateForm(forms.ModelForm):
    class Meta:
        model = Wiese
        fields = [
            'name',
            'obstwiese',
            'bluehwiese',
        ]
