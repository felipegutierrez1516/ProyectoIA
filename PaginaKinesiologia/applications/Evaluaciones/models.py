from django.db import models
from applications.Estudiante.models import *
from applications.Caso_Clínico.models import *

# Create your models here.

class Evaluacion(models.Model):
    nombre = models.CharField('Nombre de la Evaluación', max_length=150)
    descripcion = models.TextField('Descripción')
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente_Ficticio, on_delete=models.CASCADE)
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    fecha_evaluacion = models.DateField()
    
    def __str__(self):
       return str(self.id) + '-' + self.nombre

class Respuesta_Evaluacion(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE)
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    descripcion = models.TextField('Detalle')
    respuestas = models.TextField('Respuesta del estudiante')
    retroalimentacion = models.TextField('Retroalimentación')
    correcta = models.BooleanField('¿Correcta?')
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    puntaje_obtenido = models.FloatField('Puntaje', default=0)

    def __str__(self):
        return str(self.id) + '-' + self.nombre