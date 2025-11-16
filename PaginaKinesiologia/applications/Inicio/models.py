from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    TIPO_USUARIO = (
        ('estudiante', 'Estudiante'),
        ('docente', 'Docente'),
    )
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO, default='estudiante')

    def __str__(self):
        return f'{self.user.username} - {self.tipo}'
