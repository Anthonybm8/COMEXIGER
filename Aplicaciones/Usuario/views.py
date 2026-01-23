from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuario
from .models import Usuario, Mesa


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
    mesas = Mesa.objects.all().order_by("nombre")
    return render(request, "usuariore.html", {"usuario": listadoUsuarios, "mesas": mesas})



def nuevo_usuario(request):
    mesas = Mesa.objects.all().order_by("nombre")
    return render(request, "nuevo_usuario.html", {"mesas": mesas})
def guardar_mesa(request):
    if request.method == "POST":
        nombre = (request.POST.get("nombre") or "").strip()

        if not nombre:
            messages.error(request, "Ingrese el nombre de la mesa.")
            return redirect("nuevo_usuario")

        if Mesa.objects.filter(nombre__iexact=nombre).exists():
            messages.warning(request, "Esa mesa ya existe.")
            return redirect("nuevo_usuario")

        Mesa.objects.create(nombre=nombre)
        messages.success(request, "Mesa agregada correctamente.")
        return redirect("nuevo_usuario")

    return redirect("nuevo_usuario")

def guardar_usuario(request):
    if request.method == "POST":
        nombres = request.POST["nombres"]
        apellidos = request.POST["apellidos"]
        mesa = request.POST["mesa"]  # <-- sigue siendo TEXTO
        cargo = request.POST["cargo"]
        username = request.POST["username"]
        password = request.POST["password"]

        u = Usuario(
            nombres=nombres,
            apellidos=apellidos,
            mesa=mesa,
            cargo=cargo,
            username=username,
        )
        u.set_password(password)  # ✅ hashea usando tu método del modelo
        u.save()

        messages.success(request, "Usuario guardado exitosamente.")
        return redirect("usuariore")

    messages.error(request, "Error al guardar usuario.")
    return redirect("nuevo_usuario")



def eliminar_usuario(request, id):
    try:
        usuario_eliminar = Usuario.objects.get(id=id)
        usuario_eliminar.delete()
        messages.success(request, "Usuario eliminado exitosamente.")
    except Usuario.DoesNotExist:
        messages.error(request, "El usuario no existe.")
    return redirect("usuariore")


def procesar_edicion_usuario(request):
    """
    ✅ Edita: nombres, apellidos, mesa, cargo, username
    ✅ Password ES OPCIONAL:
       - Si viene vacío: no se cambia
       - Si viene con texto: se actualiza (hasheado con set_password)
    """
    if request.method == "POST":
        try:
            id = request.POST["id"]
            usuario = Usuario.objects.get(id=id)

            # Datos generales
            usuario.nombres = (request.POST.get("nombres") or "").strip()
            usuario.apellidos = (request.POST.get("apellidos") or "").strip()
            usuario.mesa = (request.POST.get("mesa") or "").strip()
            usuario.cargo = (request.POST.get("cargo") or "").strip()

            # Username (usuario) editable
            nuevo_username = (request.POST.get("username") or "").strip()

            if not nuevo_username:
                messages.error(request, "El usuario (username) es obligatorio.")
                return redirect("usuariore")

            # Validar que no exista ese username en OTRO usuario
            if Usuario.objects.filter(username__iexact=nuevo_username).exclude(id=usuario.id).exists():
                messages.error(request, "Ese usuario (username) ya está registrado. Elige otro.")
                return redirect("usuariore")

            usuario.username = nuevo_username

            # Password opcional
            nueva_password = (request.POST.get("password") or "").strip()
            if nueva_password:  # solo si viene algo escrito
                usuario.set_password(nueva_password)

            usuario.save()
            messages.success(request, "Usuario actualizado correctamente")

        except Usuario.DoesNotExist:
            messages.error(request, "El usuario no existe.")
        except Exception as e:
            messages.error(request, f"Error al procesar la edición: {e}")

    return redirect("usuariore")

