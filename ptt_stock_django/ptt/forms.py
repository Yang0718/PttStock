from django import forms
from .models import Ptt


class PttForm(forms.ModelForm):
    
    class Meta:
        model=Ptt
        fields=['Title', 'Author', 'Target', 'Label', 'Date', 'Like', 'Dislike', 'Neutral', 'url', 'ROI_1d','ROI_overall','Price']

