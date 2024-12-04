from rest_framework import serializers
from .models import Dashboard, Data
        
class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = '__all__'
        
class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        fields = '__all__'