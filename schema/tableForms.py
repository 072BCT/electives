from django import forms

from .forms import *
from .models import *
from .run_raw_sql import run_query

class belongs_toDataForm(forms.Form):
	choices = ['roll_no', 'name']
	roll_no = forms.ChoiceField(choices=choices)
	batch_num = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}), initial='Batch')

