from django.contrib import admin
from .models import MeasurementUnit, Label

admin.site.register(MeasurementUnit)
admin.site.register(Label)