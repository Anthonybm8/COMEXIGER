from django.shortcuts import render, redirect
from django.contrib import messages

def inicio(request):
    if request.method == "POST":
        usuario = request.POST.get("usuario")
        contrasena = request.POST.get("contrasena")

        if usuario == "comexad" and contrasena == "Comexiger2025":
            messages.success(request, "BIENVENIDO ADMINISTRADOR")
            return render(request, "disponibilidad.html", {"usuario": usuario})
        else:
            messages.success(request, "Credenciales incorrectas") 
            return render(request, "iniciose.html")
    return render(request, "iniciose.html")
def cerrarsesion(request):
    request.session.flush()
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("iniciose")
