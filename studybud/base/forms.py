from django.forms import ModelForm
from .models import Room
from django.contrib.auth.models import User

class RoomForm(ModelForm): #Creates a form based on the Room Model and its fields in models.py
    class Meta:
        model = Room
        fields =  '__all__'
        exclude = ['host', 'participants']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']