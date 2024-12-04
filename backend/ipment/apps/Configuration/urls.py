from django.urls import re_path as url
from apps.Configuration.views import MeasurementUnitView, LabelView

urlpatterns = [
    # Measurement Unit URL
    url(r'^(?P<method>create|list|view|update|delete)/unit/$', MeasurementUnitView.measurementUnitApi),
    url(r'^view/unit/(?P<id>[0-9]+)$', MeasurementUnitView.measurementUnitApi),
    
    # Label URL
    url(r'^(?P<method>create|list|view|update|delete)/label/$', LabelView.labelApi),
    url(r'^view/label/(?P<id>[0-9]+)$', LabelView.labelApi),
]