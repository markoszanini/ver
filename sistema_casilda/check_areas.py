from organigrama.models import Area, Funcionario
from django.contrib.auth.models import User

print("Areas:")
for a in Area.objects.all():
    print(f"- {a.nombre}")

print("\nFuncionarios y sus perfiles:")
for f in Funcionario.objects.all():
    user_str = f"User: {f.user.username}" if f.user else "No User"
    area_str = f"Area: {f.area.nombre}" if f.area else "No Area"
    depto_str = f"Depto: {f.departamento.nombre}" if f.departamento else "No Depto"
    oficina_str = f"Oficina: {f.oficina.nombre}" if f.oficina else "No Oficina"
    print(f"- {f.usuario_login} | {user_str} | {area_str} | {depto_str} | {oficina_str}")

print("\nAdmin user:")
admin = User.objects.filter(username='admin').first()
if admin:
    f = getattr(admin, 'funcionario_link', None)
    if f:
        print(f"Admin is linked to {f.usuario_login}")
    else:
        print("Admin has NO funcionario_link")
else:
    print("User 'admin' does not exist")
