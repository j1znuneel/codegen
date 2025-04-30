import ast
import os
from pathlib import Path

# Set your input and output paths
MODELS_PATH = Path("models.py")

# Output files (can be modified to write to disk if needed)
SERIALIZERS_FILE = "serializers.py"
VIEWS_FILE = "views.py"
URLS_FILE = "urls.py"

def parse_models(file_path):
    with open(file_path, "r") as f:
        tree = ast.parse(f.read())

    models = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if (
                    isinstance(base, ast.Attribute) and base.attr == "Model"
                ) or (
                    isinstance(base, ast.Name) and base.id == "Model"
                ):
                    models.append(node.name)

    return models

def generate_serializers(models):
    header = "from rest_framework import serializers\nfrom .models import " + ", ".join(models) + "\n\n"
    body = ""
    for model in models:
        body += f"class {model}Serializer(serializers.ModelSerializer):\n"
        body += f"    class Meta:\n"
        body += f"        model = {model}\n"
        body += f"        fields = '__all__'\n\n"
    return header + body

def generate_views(models):
    header = "from rest_framework import viewsets\nfrom .models import " + ", ".join(models) + "\n"
    header += "from .serializers import " + ", ".join(f"{m}Serializer" for m in models) + "\n\n"
    body = ""
    for model in models:
        body += f"class {model}ViewSet(viewsets.ModelViewSet):\n"
        body += f"    queryset = {model}.objects.all()\n"
        body += f"    serializer_class = {model}Serializer\n\n"
    return header + body

def generate_urls(models):
    header = "from rest_framework.routers import DefaultRouter\n"
    header += "from .views import " + ", ".join(f"{m}ViewSet" for m in models) + "\n\n"
    body = "router = DefaultRouter()\n"
    for model in models:
        endpoint = model.lower() + "s"
        body += f"router.register(r'{endpoint}', {model}ViewSet)\n"
    body += "\nurlpatterns = router.urls\n"
    return header + body

def write_or_print(file_name, content, to_disk=False):
    if to_disk:
        with open(file_name, "w") as f:
            f.write(content)
        print(f"✅ {file_name} written.")
    else:
        print(f"\n=== {file_name} ===\n")
        print(content)

if __name__ == "__main__":
    models = parse_models(MODELS_PATH)

    if not models:
        print("❌ No Django models found.")
        exit(1)

    serializers_code = generate_serializers(models)
    views_code = generate_views(models)
    urls_code = generate_urls(models)

    # Change to True to write to disk
    write_to_disk = True

    write_or_print(SERIALIZERS_FILE, serializers_code, write_to_disk)
    write_or_print(VIEWS_FILE, views_code, write_to_disk)
    write_or_print(URLS_FILE, urls_code, write_to_disk)
