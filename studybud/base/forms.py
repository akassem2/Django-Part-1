from django.forms import ModelForm
from .models import Room

class RoomForm(ModelForm): #Creates a form based on the Room Model and its fields in models.py
    class Meta:
        model = Room
        fields =  '__all__'
        exclude = ['host', 'participants']