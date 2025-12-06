from django.contrib import admin
from .models import Perfil, Estudiante, Docente

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol')
    list_filter = ('rol',)
    search_fields = ('user__username', 'user__email')

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('get_nombre', 'curso_activo')
    
    def get_nombre(self, obj):
        return obj.perfil.user.get_full_name()
    get_nombre.short_description = 'Nombre Completo'

admin.site.register(Docente)