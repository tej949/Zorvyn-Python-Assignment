"""Transaction models for Finance System Backend"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class Transaction(models.Model):
    """Model for financial transactions"""
    
    TYPE_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    
    CATEGORY_CHOICES = [(cat, cat.title()) for cat in settings.FINANCE_CATEGORIES]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Transaction amount in currency'
    )
    
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        help_text='Transaction type: income or expense'
    )
    
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        help_text='Transaction category for organization'
    )
    
    date = models.DateField(
        help_text='Date of the transaction'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        help_text='Additional notes about the transaction'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transactions_transaction'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', '-date']),
            models.Index(fields=['user', 'type']),
            models.Index(fields=['user', 'category']),
        ]
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.amount} ({self.category})"
    
    @property
    def is_income(self):
        """Check if transaction is income"""
        return self.type == 'income'
    
    @property
    def is_expense(self):
        """Check if transaction is expense"""
        return self.type == 'expense'
