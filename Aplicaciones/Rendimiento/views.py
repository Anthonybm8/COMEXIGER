from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from .models import Rendimiento
# Create your views here.

def inicio(request):
    listadoRendimiento=Rendimiento.objects.all()
    return render(request, 'rendimiento.html',{'rendimiento':listadoRendimiento})

def nuevo_rendimiento(request):
    return render(request, "nuevo_rendimiento.html")

def guardar_rendimiento(request):
    if request.method == "POST":
        numero_mesa = request.POST["numero_mesa"]
        variedad = request.POST["variedad"]
        medida = request.POST["medida"]
        bonches = request.POST["bonches"]
        fecha_entrada = request.POST["fecha_entrada"]
        fecha_salida = request.POST["fecha_salida"]

        nuevo = Rendimiento.objects.create(
            numero_mesa=numero_mesa,
            variedad=variedad,
            medida=medida,
            bonches=bonches,
            fecha_entrada=fecha_entrada,
            fecha_salida=fecha_salida if fecha_salida else None
        )

        messages.success(request, "Rendimiento guardado exitosamente")
        return redirect('rendimiento')
    else:
        messages.error(request, "Error al guardar rendimiento")
        return redirect('nuevo_rendimiento')

def eliminar_rendimiento(request, id):
    rendimiento_eliminar = Rendimiento.objects.get(id=id)
    rendimiento_eliminar.delete()
    messages.success(request, "Rendimiento eliminado exitosamente")
    return redirect('rendimiento')

def procesar_edicion_rendimiento(request):
    if request.method == "POST":
        try:
            id = request.POST["id"]
            rendimiento = Rendimiento.objects.get(id=id)

            rendimiento.numero_mesa = request.POST["numero_mesa"]
            rendimiento.variedad = request.POST["variedad"]
            rendimiento.medida = request.POST["medida"]
            rendimiento.bonches = request.POST["bonches"]

            fecha_entrada = request.POST.get("fecha_entrada")
            fecha_salida = request.POST.get("fecha_salida")

            if fecha_entrada:
                rendimiento.fecha_entrada = datetime.strptime(fecha_entrada, "%Y-%m-%dT%H:%M")
            if fecha_salida:
                rendimiento.fecha_salida = datetime.strptime(fecha_salida, "%Y-%m-%dT%H:%M")
            else:
                rendimiento.fecha_salida = None

            rendimiento.save()
            messages.success(request, "Rendimiento actualizado correctamente ")
        except Exception as e:
            messages.error(request, f"Error al procesar la edición: {e}")
        return redirect('rendimiento')
