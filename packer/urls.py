from django.urls import path
from .views import pack, health

urlpatterns = [
    path("health", health, name="health"),  # GET /health
    path("pack", pack, name="pack"),        # POST /pack
]
print("Loaded packer.urls:", [str(p.pattern) for p in urlpatterns])