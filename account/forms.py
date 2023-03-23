from django import forms
from .models import Account



class RegistrationForm(forms.ModelForm):
    password= forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder':'Ingrese clave',
        'class':'form-control',
        }
    ))

    confirm_password= forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder':'Ingrese clave nuevamente',
                   'class':'form-control',
        }
    ))
    class Meta:
        model=Account
        fields=['first_name','last_name','phone_number','email','password']
    
    def __init__(self,*args,**kwars):
        super(RegistrationForm,self).__init__(*args,**kwars)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'
        self.fields['first_name'].widget.attrs['placeholder']='Ingrese Nombre'
        self.fields['last_name'].widget.attrs['placeholder']='Ingrese Apellido'
        self.fields['phone_number'].widget.attrs['placeholder']='Ingrese Fono'
        self.fields['email'].widget.attrs['placeholder']='Ingrese correo'


    def clean(self):
        data=super(RegistrationForm,self).clean()
        password=data['password']
        confirm_password=data['confirm_password']    
        if password!= confirm_password:   
            raise forms.ValidationError(
                "Claves no coinciden"
            )

