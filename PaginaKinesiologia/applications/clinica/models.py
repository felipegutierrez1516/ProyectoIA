from django.db import models
from applications.clinica.models import Categoria_Clinica

# Create your models here.

class Paciente_Ficticio(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    edad = models.IntegerField()
    genero = models.CharField(max_length=50)
    categoria = models.ForeignKey(Categoria_Clinica, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.nombre}"


class Etapa(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    video = models.URLField()
    paciente = models.ForeignKey(Paciente_Ficticio, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.nombre}"


class Tema_Interrogacion(models.Model):
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=500)
    pregunta = models.CharField(max_length=500)
    respuesta = models.CharField(max_length=500)
    retroalimentacion = models.TextField()
    correcta = models.BooleanField(default=False)
    dificultad = models.CharField(max_length=10, choices=[('baja','Baja'),('media','Media'),('alta','Alta')])

    def __str__(self):
        return f"{self.id} - {self.nombre}"


class Partes_del_Cuerpo(models.Model):
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='partes_cuerpo/')
    ubicacion_anatomica = models.CharField(max_length=150)
    funcion = models.TextField(blank=True)
    correcta = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} - {self.nombre}"