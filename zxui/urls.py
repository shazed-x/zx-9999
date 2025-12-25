from django.urls import path

from .views import composer, export_data, import_export, library, manage, overview

app_name = 'zxui'

urlpatterns = [
    path('', overview, name='overview'),
    path('composer/', composer, name='composer'),
    path('library/', library, name='library'),
    path('manage/', manage, name='manage'),
    path('import/', import_export, name='import_export'),
    path('export/', export_data, name='export'),
]
