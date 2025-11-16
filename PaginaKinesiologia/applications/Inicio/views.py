from django.shortcuts import render

# Create your views here.
from django.views.generic import (
    TemplateView,
)

class vistaInicio(TemplateView):
    template_name='inicio/inicio.html'