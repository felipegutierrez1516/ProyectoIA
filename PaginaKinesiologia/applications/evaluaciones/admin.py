from django.contrib import admin
from .models import Evaluacion, Respuesta_Evaluacion

# --- INLINE PARA VER LAS RESPUESTAS DENTRO DE LA EVALUACIÓN ---
class RespuestaInline(admin.TabularInline):
    model = Respuesta_Evaluacion
    extra = 0 # No mostrar filas vacías extra
    # Hacemos los campos de solo lectura para que el admin pueda ver qué respondió el alumno sin modificarlo por error
    readonly_fields = ('etapa', 'descripcion', 'respuesta_estudiante', 'retroalimentacion', 'correcta', 'puntaje_obtenido')
    can_delete = False 
    classes = ['collapse'] # Permite colapsar esta sección si hay muchas respuestas

# --- CONFIGURACIÓN PRINCIPAL ---

@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    # Qué columnas mostrar en la lista
    list_display = ('id', 'estudiante_nombre', 'paciente', 'estado', 'fecha_evaluacion', 'puntaje_diagnostico')
    
    # Menú lateral para filtrar
    list_filter = ('estado', 'fecha_evaluacion', 'paciente__caso__curso')
    
    # Barra de búsqueda (busca por nombre del alumno o del paciente)
    search_fields = ('estudiante__perfil__user__first_name', 'estudiante__perfil__user__last_name', 'paciente__nombre')
    
    # Ordenar por fecha descendente
    ordering = ('-fecha_evaluacion',)

    # Navegación jerárquica por fechas (Año > Mes > Día) en la parte superior
    date_hierarchy = 'fecha_evaluacion'

    # Agregamos las respuestas dentro de la misma pantalla
    inlines = [RespuestaInline]

    # Organización visual del formulario en secciones
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'estado', 'fecha_evaluacion')
        }),
        ('Participantes', {
            'fields': ('estudiante', 'paciente')
        }),
        ('Resultados Automáticos', {
            'fields': ('diagnostico', 'tiempo_total', 'respuestas_correctas_primer_intento'),
            'classes': ('collapse',), # Esta sección inicia cerrada para ahorrar espacio
        }),
        ('Revisión Docente', {
            'fields': ('puntaje_diagnostico', 'comentario_docente'),
            'description': 'Espacio reservado para la calificación manual del docente.'
        }),
    )

    # Método para mostrar nombre bonito del estudiante
    def estudiante_nombre(self, obj):
        return f"{obj.estudiante.perfil.user.first_name} {obj.estudiante.perfil.user.last_name}"
    estudiante_nombre.short_description = 'Estudiante'

@admin.register(Respuesta_Evaluacion)
class RespuestaEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'evaluacion_info', 'etapa', 'correcta', 'puntaje_obtenido')
    list_filter = ('correcta', 'etapa__nombre')
    search_fields = ('descripcion', 'respuesta_estudiante', 'evaluacion__estudiante__perfil__user__first_name')

    def evaluacion_info(self, obj):
        return f"{obj.evaluacion.estudiante} - {obj.evaluacion.paciente}"
    evaluacion_info.short_description = 'Evaluación'