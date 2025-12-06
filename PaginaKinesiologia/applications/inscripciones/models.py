from django.db import models
from applications.usuarios.models import Estudiante
from applications.cursos.models import Curso

# Create your models here.


class Solicitud_Inscripcion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    estado = models.CharField(max_length=10, choices=[('pendiente','Pendiente'),('aceptada','Aceptada'),('rechazada','Rechazada')])
    comentario = models.TextField(blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}"
    
    class Meta:
        verbose_name = "Solicitud de Inscripción"
        verbose_name_plural = "Solicitudes de Inscripción"