from django.shortcuts import render,redirect
from django.contrib import messages

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from Aplicaciones.Rendimiento.models import Rendimiento

def inicio(request):
    return render(request,"disponibilidad.html")

@require_GET
def rendimientos_json(request):
    qs = Rendimiento.objects.values(
        'id',
        'numero_mesa',
        'variedad',
        'medida',
        'bonches',
        'fecha_entrada',
        'fecha_salida',
        'codigo_id',
    ).order_by('-fecha_entrada')[:500]  # opcional: limit
    return JsonResponse(list(qs), safe=False, json_dumps_params={'default': str})
