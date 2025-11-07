from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuario

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

def inicios(request):
    listadoUsuarios = Usuario.objects.all()
    return render(request,"usuariore.html", {'usuario': listadoUsuarios})

def nuevo_usuario(request):
    return render(request, "nuevo_usuario.html")

def guardar_usuario(request):
    if request.method == "POST":
        nombres = request.POST["nombres"]
        apellidos = request.POST["apellidos"]
        mesa = request.POST["mesa"]
        cargo = request.POST["cargo"]
        Usuario.objects.create(
            nombres=nombres,
            apellidos=apellidos,
            mesa=mesa,
            cargo=cargo
        )
        messages.success(request, "Usuario guardado exitosamente ")
        return redirect('usuariore')
    else:
        messages.error(request, "Error al guardar usuario ")
        return redirect('nuevo_usuario')

def eliminar_usuario(request, id):
    try:
        usuario_eliminar = Usuario.objects.get(id=id)
        usuario_eliminar.delete()
        messages.success(request, "Usuario eliminado exitosamente ")
    except Usuario.DoesNotExist:
        messages.error(request, "El usuario no existe ")
    return redirect('usuariore')


def procesar_edicion_usuario(request):
    if request.method == "POST":
        try:
            id = request.POST["id"]
            usuario = Usuario.objects.get(id=id)

            usuario.nombres = request.POST["nombres"]
            usuario.apellidos = request.POST["apellidos"]
            usuario.mesa = request.POST["mesa"]
            usuario.cargo = request.POST["cargo"]

            usuario.save()
            messages.success(request, "Usuario actualizado correctamente")

        except Exception as e:
            messages.error(request, f"Error al procesar la edición: {e}")

        return redirect('usuariore')
