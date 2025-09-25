from django.shortcuts import render, redirect
from django.contrib import messages

def inicio(request):
    if request.method == "POST":
        usuario = request.POST.get("usuario")
        contrasena = request.POST.get("contrasena")

        if usuario == "comexad" and contrasena == "Comexiger2025":
            return render(request, "disponibilidad.html", {"usuario": usuario})
        else:
            return render(request, "iniciose.html", {"error": "Credenciales incorrectas"})
    return render(request, "iniciose.html")
def cerrarsesion(request):
    request.session.flush()
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("iniciose")
