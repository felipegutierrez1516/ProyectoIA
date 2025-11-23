from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Caso)
admin.site.register(Paciente_Ficticio)
admin.site.register(Etapa)
admin.site.register(Tema_Interrogacion)


from django import forms
from .models import Partes_del_Cuerpo, COORDS_MAP

class PartesForm(forms.ModelForm):
    class Meta:
        model = Partes_del_Cuerpo
        fields = ['etapa', 'nombre', 'descripcion', 'left', 'top', 'correcta']

    def clean(self):
        cleaned = super().clean()
        nombre = (cleaned.get('nombre') or '').strip().lower()
        left = cleaned.get('left') or 0
        top = cleaned.get('top') or 0
        if left == 0 and top == 0 and nombre in COORDS_MAP:
            cleaned['left'], cleaned['top'] = COORDS_MAP[nombre]
        return cleaned

class PartesDelCuerpoAdmin(admin.ModelAdmin):
    form = PartesForm
    class Media:
        js = ('js/ubicacion_automatica.js',)

admin.site.register(Partes_del_Cuerpo, PartesDelCuerpoAdmin)
