from django.db import models
from applications.usuarios.models import Estudiante
from applications.cursos.models import Curso

# Create your models here.

class Progreso(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    descripcion = models.TextField()
    porcentaje_avance = models.FloatField()
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"