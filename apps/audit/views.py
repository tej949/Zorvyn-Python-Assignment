"""Views for Audit app"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer
from apps.users.permissions import IsAdmin
from utils.csv_export import export_audit_logs_to_csv


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for audit logs (read-only)"""
    
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'action', 'model']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Get queryset based on permissions"""
        if self.request.user.is_admin():
            return AuditLog.objects.all()
        
        # Regular users can only see their own logs
        return AuditLog.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """List audit logs"""
        if not request.user.is_admin():
            return Response(
                {
                    'error': True,
                    'message': 'You do not have permission to view audit logs.',
                    'code': 'forbidden',
                    'status': status.HTTP_403_FORBIDDEN,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export audit logs to CSV"""
        if not request.user.is_admin():
            return Response(
                {
                    'error': True,
                    'message': 'You do not have permission to export audit logs.',
                    'code': 'forbidden',
                    'status': status.HTTP_403_FORBIDDEN,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        
        return export_audit_logs_to_csv(queryset)
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Get audit logs for a specific user"""
        if not request.user.is_admin():
            return Response(
                {
                    'error': True,
                    'message': 'You do not have permission to view user audit logs.',
                    'code': 'forbidden',
                    'status': status.HTTP_403_FORBIDDEN,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {
                    'error': True,
                    'message': 'user_id parameter is required.',
                    'code': 'validation_error',
                    'status': status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        logs = AuditLog.objects.filter(user_id=user_id).order_by('-timestamp')
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(
            {
                'error': False,
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @action(detail=False, methods=['get'])
    def by_action(self, request):
        """Get audit logs for a specific action"""
        if not request.user.is_admin():
            return Response(
                {
                    'error': True,
                    'message': 'You do not have permission to view audit logs.',
                    'code': 'forbidden',
                    'status': status.HTTP_403_FORBIDDEN,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        action = request.query_params.get('action')
        
        if not action:
            return Response(
                {
                    'error': True,
                    'message': 'action parameter is required.',
                    'code': 'validation_error',
                    'status': status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        logs = AuditLog.objects.filter(action=action).order_by('-timestamp')
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(
            {
                'error': False,
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )
