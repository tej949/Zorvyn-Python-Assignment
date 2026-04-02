"""Serializers for Transactions app"""
from rest_framework import serializers
from apps.transactions.models import Transaction
from django.conf import settings


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transactions"""
    
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'user',
            'username',
            'amount',
            'type',
            'type_display',
            'category',
            'category_display',
            'date',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_amount(self, value):
        """Validate amount"""
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than 0.')
        return value
    
    def validate(self, data):
        """Validate transaction data"""
        if data.get('category') not in dict(Transaction.CATEGORY_CHOICES):
            raise serializers.ValidationError({'category': 'Invalid category.'})
        return data


class TransactionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating transactions"""
    
    class Meta:
        model = Transaction
        fields = [
            'amount',
            'type',
            'category',
            'date',
            'description',
        ]


class TransactionListSerializer(serializers.ModelSerializer):
    """Serializer for listing transactions"""
    
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'amount',
            'type',
            'type_display',
            'category',
            'category_display',
            'date',
            'created_at',
        ]
        read_only_fields = fields


class TransactionDetailSerializer(serializers.ModelSerializer):
    """Serializer for transaction details"""
    
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'username',
            'amount',
            'type',
            'type_display',
            'category',
            'category_display',
            'date',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'username', 'created_at', 'updated_at']


class BulkTransactionSerializer(serializers.Serializer):
    """Serializer for bulk operations"""
    
    transaction_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text='List of transaction IDs to operate on'
    )
