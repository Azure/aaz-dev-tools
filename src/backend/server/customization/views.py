from django.shortcuts import render
from rest_framework import viewsets
from .serializers import CustomizationSerializer
from .models import Customization

# Create your views here.

class CustomizationView(viewsets.ModelViewSet):
    serializer_class = CustomizationSerializer
    queryset = Customization.objects.all()