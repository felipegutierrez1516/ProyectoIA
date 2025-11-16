from django.db import models
from applications.Cursos.models import *
from applications.Evaluaciones.models import *

# Create your models here.

class Envio_Docente(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    respuesta_evaluacion = models.ForeignKey(Respuesta_Evaluacion, on_delete=models.CASCADE)
    nombre = models.CharField('Nombre de la Evaluación', max_length=150)
    descripcion = models.TextField('Descripción')
    nombre_estudiante = models.TextField('Nombre del Estudiante')
    fecha_entrega = models.DateField()
    estado_revision = models.CharField('Estado', max_length=15, choices=[('pendiente', 'Pendiente'), ('revisado', 'Revisado'), ('aprobado', 'Aprobado')])
    comentario_docente = models.TextField('Comentario del Docente', blank=True)

    def __str__(self):
        return str(self.id) + '-' + self.nombre