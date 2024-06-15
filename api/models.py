# Create your models here.
from django.db import models
from django.utils import timezone

class Pago(models.Model):
    codigo = models.CharField(max_length=100)
    estado = models.IntegerField()
    fec_crea = models.DateTimeField(default=timezone.now)
    fec_update = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Pago {self.codigo} - Estado {self.estado}"
    
class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.CharField(max_length=100)
    pass_field = models.CharField(db_column='pass', max_length=40)  

    class Meta:
        db_table = 'usuario'

class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    stock = models.IntegerField(default=0)
    precio= models.IntegerField(default=0.0)
    class Meta:
        db_table = 'producto'