from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'cedula', 'email', 'rol', 'cargo', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('cedula', 'cargo', 'unidad_pertenencia', 'rol')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
