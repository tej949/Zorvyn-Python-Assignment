"""Views for Transactions app"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.transactions.models import Transaction
from apps.transactions.serializers import (
    TransactionSerializer,
    TransactionCreateUpdateSerializer,
    TransactionListSerializer,
    TransactionDetailSerializer,
)
from apps.transactions.filters import TransactionFilter
from apps.transactions.permissions import (
    IsOwnerOrAdmin,
    CanExportTransactions,
    CanCreateTransaction,
)
from utils.csv_export import export_transactions_to_csv


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for transaction management"""
    
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = TransactionFilter
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']
    pagination_class = None  # Will use default from settings
    
    def get_queryset(self):
        """Get queryset based on permissions"""
        user = self.request.user
        
        if user.is_admin():
            # Admin can see all transactions
            return Transaction.objects.all()
        
        # Other users can only see their own transactions
        return Transaction.objects.filter(user=user)
    
    def get_serializer_class(self):
        """Get serializer based on action"""
        if self.action in ['create', 'update', 'partial_update']:
            return TransactionCreateUpdateSerializer
        elif self.action == 'list':
            return TransactionListSerializer
        elif self.action == 'retrieve':
            return TransactionDetailSerializer
        return TransactionSerializer
    
    def perform_create(self, serializer):
        """Create transaction and assign user"""
        user = self.request.user
        
        # Admin can create for other users, otherwise assign to self
        if user.is_admin() and 'user' in self.request.data:
            user_id = self.request.data.get('user')
            try:
                user = user.__class__.objects.get(id=user_id)
            except user.__class__.DoesNotExist:
                return Response(
                    {
                        'error': True,
                        'message': 'User not found.',
                        'code': 'not_found',
                        'status': status.HTTP_404_NOT_FOUND,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
        
        serializer.save(user=user)
    
    def create(self, request, *args, **kwargs):
        """Create a new transaction"""
        # Check permission to create
        if not (request.user.is_analyst() or request.user.is_admin()):
            return Response(
                {
                    'error': True,
                    'message': 'You do not have permission to create transactions.',
                    'code': 'forbidden',
                    'status': status.HTTP_403_FORBIDDEN,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, CanExportTransactions])
    def export_csv(self, request):
        """Export transactions to CSV"""
        queryset = self.get_queryset()
        
        # Apply filters
        queryset = self.filter_queryset(queryset)
        
        return export_transactions_to_csv(queryset)
    
    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """Get detailed information about a transaction"""
        transaction = self.get_object()
        
        # Check permission
        if transaction.user != request.user and not request.user.is_admin():
            return Response(
                {
                    'error': True,
                    'message': 'You do not have permission to view this transaction.',
                    'code': 'forbidden',
                    'status': status.HTTP_403_FORBIDDEN,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        serializer = TransactionDetailSerializer(transaction)
        return Response(
            {
                'error': False,
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific transaction"""
        transaction = self.get_object()
        
        # Check permission
        if transaction.user != request.user and not request.user.is_admin():
            return Response(
                {
                    'error': True,
                    'message': 'You do not have permission to view this transaction.',
                    'code': 'forbidden',
                    'status': status.HTTP_403_FORBIDDEN,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        
        serializer = self.get_serializer(transaction)
        return Response(
            {
                'error': False,
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    def list(self, request, *args, **kwargs):
        """List transactions with pagination"""
        return super().list(request, *args, **kwargs)
