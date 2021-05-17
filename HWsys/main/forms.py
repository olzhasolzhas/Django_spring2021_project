from django import forms

from .models import Homework


class HwForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ('deadline', 'lesson', 'file')
