from django.contrib import admin

from .models import System


class AdminSystem(admin.ModelAdmin):
    pass


admin.site.register(System, AdminSystem)
