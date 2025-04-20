from django.contrib import admin
from django.urls import path, include  # 👈 import include to allow app routing

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # 👈 include accounts app URLs
]
