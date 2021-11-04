from django.contrib import admin
from .models import Customization

# Register your models here.
class CustomizationAdmin(admin.ModelAdmin):
    list_display = ('module_name', 'module_path')

admin.site.register(Customization, CustomizationAdmin)