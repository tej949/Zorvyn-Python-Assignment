"""
URL configuration for Finance System Backend
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/', include([
        path('auth/', include('apps.users.urls')),
        path('transactions/', include('apps.transactions.urls')),
        path('analytics/', include('apps.analytics.urls')),
        path('audit-logs/', include('apps.audit.urls')),
        path('users/', include('apps.users.urls_users')),
    ])),
    
    # Health check
    path('health/', lambda request: __import__('django.http').http.JsonResponse({'status': 'ok'})),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
