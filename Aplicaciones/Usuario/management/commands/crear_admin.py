from django.core.management.base import BaseCommand
from Aplicaciones.Usuario.models import Usuario

class Command(BaseCommand):
    help = "Crea un usuario ADMIN para la web si no existe"

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--nombres", default="Admin")
        parser.add_argument("--apellidos", default="Web")
    
        parser.add_argument("--mesa", default="")
        parser.add_argument("--cargo", default="ADMIN")

    def handle(self, *args, **opts):
        username = opts["username"].strip()
        mesa = (opts.get("mesa") or "").strip()
        cargo = (opts.get("cargo") or "ADMIN").strip()

   
        if cargo.upper() == "ADMIN":
            mesa = ""

        u = Usuario.objects.filter(username__iexact=username).first()

        if u:
            u.nombres = opts["nombres"]
            u.apellidos = opts["apellidos"]
            u.mesa = mesa
            u.cargo = cargo
            u.set_password(opts["password"])
            u.save()
            self.stdout.write(self.style.SUCCESS(f" Admin actualizado: {u.username}"))
            return

        u = Usuario(
            nombres=opts["nombres"],
            apellidos=opts["apellidos"],
            mesa=mesa,
            cargo=cargo,
            username=username,
        )
        u.set_password(opts["password"])
        u.save()
        self.stdout.write(self.style.SUCCESS(f"Admin creado: {u.username}"))
