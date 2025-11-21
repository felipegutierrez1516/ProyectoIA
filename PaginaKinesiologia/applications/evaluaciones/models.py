from django.db import models
from applications.clinica.models import Paciente_Ficticio, Etapa
from applications.usuarios.models import Estudiante, Docente

# Create your models here.


class Evaluacion(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente_Ficticio, on_delete=models.CASCADE)
    fecha_evaluacion = models.DateField()
    diagnostico = models.TextField()
    tiempo_total = models.DurationField()
    respuestas_correctas_primer_intento = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.id} - {self.nombre}"


class Respuesta_Evaluacion(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE)
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    descripcion = models.TextField()
    respuesta_estudiante = models.TextField()
    retroalimentacion = models.TextField()
    correcta = models.BooleanField()
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    puntaje_obtenido = models.FloatField(default=0)

    def __str__(self):
        return f"{self.id}"


class Envio_Docente(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    respuesta_evaluacion = models.ForeignKey(Respuesta_Evaluacion, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    fecha_entrega = models.DateField()
    estado_revision = models.CharField(max_length=15, choices=[('pendiente','Pendiente'),('revisado','Revisado'),('aprobado','Aprobado')])
    comentario_docente = models.TextField(blank=True)

    def __str__(self):
        return f"{self.id}"