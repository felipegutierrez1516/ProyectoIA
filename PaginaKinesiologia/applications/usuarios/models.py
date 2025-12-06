from django.db import models
from django.contrib.auth.models import User
from applications.cursos.models import Curso

# Create your models here.

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField('Rol', max_length=20, choices=[('docente','Docente'),('estudiante','Estudiante')])
    
    def __str__(self):
        return f"{self.user.username} - {self.rol}"
    
    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"



class Docente(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.perfil.user.get_full_name()}"

class Meta:
        verbose_name = "Docente"
        verbose_name_plural = "Docentes"



class Estudiante(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    modo_oscuro = models.BooleanField(default=False)
    ocultar_instrucciones = models.BooleanField(default=False)

    curso_activo = models.ForeignKey(
        'cursos.Curso', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='estudiantes_activos'
    )

    def __str__(self):
        return f"{self.id} - {self.perfil.user.get_full_name()}"
    
    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"