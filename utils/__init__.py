"""
Custom decorators for Finance System Backend
"""
from functools import wraps
from rest_framework import status
from rest_framework.response import Response
from utils.exceptions import ForbiddenException


def require_role(*allowed_roles):
    """
    Decorator to check if user has required role
    
    Usage:
        @require_role('admin', 'analyst')
        def my_view(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response(
                    {
                        'error': True,
                        'message': 'Authentication required.',
                        'code': 'unauthorized',
                        'status': status.HTTP_401_UNAUTHORIZED,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            
            if request.user.role not in allowed_roles:
                return Response(
                    {
                        'error': True,
                        'message': 'You do not have permission for this action.',
                        'code': 'forbidden',
                        'status': status.HTTP_403_FORBIDDEN,
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def handle_exceptions(view_func):
    """
    Decorator to handle exceptions in views
    
    Usage:
        @handle_exceptions
        def my_view(request):
            pass
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except ForbiddenException as e:
            return Response(
                {
                    'error': True,
                    'message': str(e.detail),
                    'code': e.default_code,
                    'status': status.HTTP_403_FORBIDDEN,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        except Exception as e:
            return Response(
                {
                    'error': True,
                    'message': 'An unexpected error occurred.',
                    'code': 'server_error',
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    return wrapper
