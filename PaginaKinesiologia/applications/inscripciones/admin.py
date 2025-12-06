from django.contrib import admin
from .models import Solicitud_Inscripcion

@admin.register(Solicitud_Inscripcion)
class SolicitudInscripcionAdmin(admin.ModelAdmin):
    # Columnas visibles (ID, Estudiante, Curso, Estado, Fecha)
    list_display = ('id', 'estudiante_nombre', 'curso', 'estado', 'fecha_solicitud')
    
    # Filtros laterales (Estado de la solicitud, Fecha, Curso específico)
    list_filter = ('estado', 'fecha_solicitud', 'curso')
    
    # Buscador (Por nombre/apellido del alumno, RUT o nombre del curso)
    search_fields = (
        'estudiante__perfil__user__first_name', 
        'estudiante__perfil__user__last_name', 
        'estudiante__perfil__rut', 
        'curso__nombre'
    )
    
    # Permite editar el estado directamente desde la lista (¡Muy útil!)
    list_editable = ('estado',) 
    
    # Ordenar por las más recientes primero
    ordering = ('-fecha_solicitud',)

    # Función para mostrar el nombre completo del estudiante
    def estudiante_nombre(self, obj):
        return f"{obj.estudiante.perfil.user.first_name} {obj.estudiante.perfil.user.last_name}"
    estudiante_nombre.short_description = 'Estudiante'