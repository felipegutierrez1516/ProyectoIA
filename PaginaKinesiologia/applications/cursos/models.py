from django.db import models
from applications.usuarios.models import Docente

# Create your models here.

class Aprendizaje_Esperado(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    nivel = models.CharField(max_length=50, choices=[('básico','Básico'),('intermedio','Intermedio'),('avanzado','Avanzado')])

    def __str__(self):
        return f"{self.id} - {self.nombre}"


class Curso(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    programa = models.TextField()
    estado = models.CharField(max_length=10, choices=[('activo','Activo'),('inactivo','Inactivo')])
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    objetivo = models.ForeignKey(Aprendizaje_Esperado, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.nombre}"


class Categoria_Clinica(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.nombre}"