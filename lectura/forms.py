
from django import forms
from crispy_forms.helper import FormHelper
from .models import Correodummy1


class  LecturaForm(forms.ModelForm):
    #https://riptutorial.com/django/example/24805/file-uploads-with-django-forms
    class Meta:
         
        model = Correodummy1
        fields = ['correo','clave']
          
              
    def __init__(self, *args, **kwargs):
        #kwargs['instance']
        

        super(LecturaForm, self).__init__(*args, **kwargs)

        
    strAttr={'class': "mb-3 bg-info "}

    correo= forms.EmailField(
        max_length=50,
        widget=forms.EmailInput(
        attrs=strAttr))
    
    clave = forms.CharField(
        max_length=12,
        widget=forms.TextInput(
        attrs=strAttr))


class CrispyLecturaForm(LecturaForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        
        self.helper = FormHelper     
        
    