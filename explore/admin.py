from django.contrib import admin

from .models import Species


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "habitat")
    list_filter = ("category",)
    search_fields = ("name", "summary", "habitat")
