from django.shortcuts import render
from rest_framework import viewsets
from .serializers import CustomizationSerializer
from .models import Customization
from rest_framework.response import Response
from rest_framework.decorators import api_view
from swagger.model.specs import SwaggerSpecs

# Create your views here.

class CustomizationView(viewsets.ModelViewSet):
    serializer_class = CustomizationSerializer
    queryset = Customization.objects.all()


def generate_specs():
    swagger_path = "C:\\Users\\zhiyihuang\\Repos\\azure-rest-api-specs"
    specs = SwaggerSpecs(folder_path=swagger_path)
    mgmt_plane_modules = specs.get_mgmt_plane_modules()
    data_plane_modules = specs.get_data_plane_modules()

    def get_module_map(modules):
        module_map = {}
        for module in modules:
            module_map[module.name] = []
            for resource_provider in module.get_resource_providers():
                for resource_id, version_map in resource_provider.get_resource_map().items():
                    module_map[module.name].append({resource_id: [k.version for k in version_map.keys()]})
        return module_map

    mgmt_plane_map = get_module_map(mgmt_plane_modules)
    data_plane_map = get_module_map(data_plane_modules)
    return [mgmt_plane_map, data_plane_map]




@api_view()
def list_specifications(request):
    specs = generate_specs()
    return Response(specs)