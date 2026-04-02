"""
URL configuration for Users app - Authentication endpoints
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import AuthenticationViewSet, UserSelfViewSet
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

router = DefaultRouter()
router.register(r'auth', AuthenticationViewSet, basename='auth')
router.register(r'self', UserSelfViewSet, basename='self')

urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]
