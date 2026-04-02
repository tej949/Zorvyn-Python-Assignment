"""Admin configuration for Transactions app"""
from django.contrib import admin
from apps.transactions.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin for Transaction model"""
    
    list_display = ['id', 'user', 'type', 'category', 'amount', 'date', 'created_at']
    list_filter = ['type', 'category', 'date', 'created_at']
    search_fields = ['user__username', 'description', 'category']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date', '-created_at']
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('user', 'amount', 'type', 'category')
        }),
        ('Details', {
            'fields': ('date', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        """Filter queryset based on user permissions"""
        qs = super().get_queryset(request)
        if not request.user.is_staff or not request.user.is_admin():
            # Regular users can only see their own transactions
            qs = qs.filter(user=request.user)
        return qs
