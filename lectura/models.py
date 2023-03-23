from django.db import models


class Correodummy1(models.Model):
    correo=models.EmailField(max_length=50)
    clave=models.CharField(max_length=12)

    

    def __str__(self):
            return self.correo
    
    class Meta:
        verbose_name='TablaDummy'
        verbose_name_plural='dumys'