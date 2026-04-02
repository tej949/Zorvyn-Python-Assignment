"""
Views for Users app
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django_filters import rest_framework as filters
from django_filters import FilterSet

from apps.users.models import User
from apps.users.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    UserListSerializer,
    ChangePasswordSerializer,
)
from apps.users.permissions import IsAdmin, IsOwnerOrAdmin


class UserFilter(FilterSet):
    """Filter for users"""
    
    class Meta:
        model = User
        fields = ['role', 'is_active']


class AuthenticationViewSet(viewsets.ViewSet):
    """ViewSet for authentication endpoints"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response(
                {
                    'error': False,
                    'message': 'User registered successfully.',
                    'user': UserDetailSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                },
                status=status.HTTP_201_CREATED,
            )
        
        return Response(
            {
                'error': True,
                'message': 'Registration failed.',
                'details': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login user"""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response(
                {
                    'error': False,
                    'message': 'Login successful.',
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                },
                status=status.HTTP_200_OK,
            )
        
        return Response(
            {
                'error': True,
                'message': 'Login failed.',
                'details': serializer.errors,
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management"""
    
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = UserFilter
    
    def get_queryset(self):
        """Get queryset based on permissions"""
        if self.request.user.is_admin():
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        """Get serializer based on action"""
        if self.action == 'list':
            return UserListSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserDetailSerializer
    
    def list(self, request, *args, **kwargs):
        """List users (admin only)"""
        if not request.user.is_admin():
            return Response(
                {
                    'error': True,
                    'message': 'You do not have permission to view user list.',
                    'code': 'forbidden',
                    'status': status.HTTP_403_FORBIDDEN,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user details"""
        serializer = UserDetailSerializer(request.user)
        return Response(
            {
                'error': False,
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def change_password(self, request, pk=None):
        """Change user password"""
        user = self.get_object()
        
        if user != request.user and not request.user.is_admin():
            return Response(
                {
                    'error': True,
                    'message': 'You can only change your own password.',
                    'code': 'forbidden',
                    'status': status.HTTP_403_FORBIDDEN,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        serializer = ChangePasswordSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'error': False,
                    'message': 'Password changed successfully.',
                },
                status=status.HTTP_200_OK,
            )
        
        return Response(
            {
                'error': True,
                'message': 'Password change failed.',
                'details': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserSelfViewSet(viewsets.ViewSet):
    """ViewSet for user self-service endpoints"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get user profile"""
        serializer = UserDetailSerializer(request.user)
        return Response(
            {
                'error': False,
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        """Update user profile"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'error': False,
                    'message': 'Profile updated successfully.',
                    'data': UserDetailSerializer(request.user).data,
                },
                status=status.HTTP_200_OK,
            )
        
        return Response(
            {
                'error': True,
                'message': 'Profile update failed.',
                'details': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
