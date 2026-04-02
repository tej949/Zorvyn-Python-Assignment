"""
Custom exception handlers for Finance System Backend
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import APIException


class FinanceSystemException(APIException):
    """Base custom exception for Finance System"""
    default_detail = 'An error occurred.'
    default_code = 'error'
    status_code = status.HTTP_400_BAD_REQUEST


class ValidationException(FinanceSystemException):
    """Raised when validation fails"""
    default_detail = 'Validation error.'
    default_code = 'validation_error'
    status_code = status.HTTP_400_BAD_REQUEST


class UnauthorizedException(FinanceSystemException):
    """Raised when user is not authenticated"""
    default_detail = 'Authentication required.'
    default_code = 'unauthorized'
    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenException(FinanceSystemException):
    """Raised when user lacks permission"""
    default_detail = 'You do not have permission to access this resource.'
    default_code = 'forbidden'
    status_code = status.HTTP_403_FORBIDDEN


class ResourceNotFoundException(FinanceSystemException):
    """Raised when resource is not found"""
    default_detail = 'Resource not found.'
    default_code = 'not_found'
    status_code = status.HTTP_404_NOT_FOUND


class ConflictException(FinanceSystemException):
    """Raised when there is a conflict"""
    default_detail = 'Conflict detected.'
    default_code = 'conflict'
    status_code = status.HTTP_409_CONFLICT


def custom_exception_handler(exc, context):
    """
    Custom exception handler for API responses
    """
    from rest_framework.views import exception_handler
    
    # Call default exception handler first to get the standard error response
    response = exception_handler(exc, context)
    
    if response is not None:
        # Add custom error format
        error_data = {
            'error': True,
            'message': response.data.get('detail', str(exc)) if hasattr(response.data, 'get') else str(exc),
            'code': getattr(exc, 'default_code', 'error'),
            'status': response.status_code,
        }
        
        # Include detailed errors if present
        if hasattr(response.data, 'items'):
            error_data['details'] = dict(response.data)
        
        response.data = error_data
    else:
        # Handle unhandled exceptions
        response = Response(
            {
                'error': True,
                'message': 'An unexpected error occurred.',
                'code': 'server_error',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
    return response
