from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField('Rol', max_length=20, choices=[('docente','Docente'),('estudiante','Estudiante')])
    
    def __str__(self):
        return f"{self.user.username} - {self.rol}"


class Docente(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.perfil.user.get_full_name()}"


class Estudiante(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.perfil.user.get_full_name()}"