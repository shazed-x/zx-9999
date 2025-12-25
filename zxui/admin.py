from django.contrib import admin

from .models import CommandTemplate, Tool


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'updated_at')
    search_fields = ('name',)


@admin.register(CommandTemplate)
class CommandTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'tool', 'category', 'updated_at')
    list_filter = ('tool', 'category')
    search_fields = ('name', 'template', 'category')
