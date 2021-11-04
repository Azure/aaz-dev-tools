from rest_framework import serializers
from .models import Customization

class CustomizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customization
        fields = ('id', 'module_name', 'module_path')