"""Analytics service logic for Finance System"""
from django.db.models import Sum, Q, Count
from apps.transactions.models import Transaction
from datetime import datetime, date, timedelta
from decimal import Decimal


class AnalyticsService:
    """Service class for financial analytics"""
    
    def __init__(self, user):
        """Initialize analytics service for a user"""
        self.user = user
    
    def get_transactions_queryset(self):
        """Get transactions queryset for the user"""
        if self.user.is_admin():
            return Transaction.objects.all()
        return Transaction.objects.filter(user=self.user)
    
    def get_summary(self):
        """Get financial summary"""
        qs = self.get_transactions_queryset()
        
        total_income = qs.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        total_expenses = qs.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        return {
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'current_balance': float(total_income - total_expenses),
            'transaction_count': qs.count(),
        }
    
    def get_category_breakdown(self):
        """Get breakdown by category"""
        qs = self.get_transactions_queryset()
        
        income_by_category = {}
        for transaction in qs.filter(type='income'):
            category = transaction.category
            income_by_category[category] = income_by_category.get(category, Decimal('0')) + transaction.amount
        
        expense_by_category = {}
        for transaction in qs.filter(type='expense'):
            category = transaction.category
            expense_by_category[category] = expense_by_category.get(category, Decimal('0')) + transaction.amount
        
        # Convert to float
        income_by_category = {k: float(v) for k, v in income_by_category.items()}
        expense_by_category = {k: float(v) for k, v in expense_by_category.items()}
        
        return {
            'income_by_category': income_by_category,
            'expense_by_category': expense_by_category,
        }
    
    def get_monthly_totals(self, year=None):
        """Get monthly totals for a given year"""
        if year is None:
            year = date.today().year
        
        qs = self.get_transactions_queryset()
        qs = qs.filter(date__year=year)
        
        # Initialize months dict
        months_data = []
        for month in range(1, 13):
            month_start = date(year, month, 1)
            if month == 12:
                month_end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(year, month + 1, 1) - timedelta(days=1)
            
            month_qs = qs.filter(date__gte=month_start, date__lte=month_end)
            
            income = month_qs.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
            expenses = month_qs.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
            
            months_data.append({
                'month': f'{year}-{month:02d}',
                'income': float(income),
                'expenses': float(expenses),
                'balance': float(income - expenses),
            })
        
        return {'months': months_data}
    
    def get_recent_activity(self, limit=10):
        """Get recent transactions"""
        qs = self.get_transactions_queryset()
        recent = qs.order_by('-date', '-created_at')[:limit]
        
        transactions = []
        for transaction in recent:
            transactions.append({
                'id': transaction.id,
                'amount': float(transaction.amount),
                'type': transaction.type,
                'category': transaction.category,
                'date': transaction.date.isoformat(),
                'description': transaction.description,
                'created_at': transaction.created_at.isoformat(),
            })
        
        return {'recent_transactions': transactions}
    
    def get_category_totals(self, transaction_type=None):
        """Get total by category"""
        qs = self.get_transactions_queryset()
        
        if transaction_type:
            qs = qs.filter(type=transaction_type)
        
        category_totals = {}
        for transaction in qs:
            category = transaction.category
            category_totals[category] = category_totals.get(category, Decimal('0')) + transaction.amount
        
        # Convert to float
        return {k: float(v) for k, v in category_totals.items()}
    
    def get_spending_trend(self, months=6):
        """Get spending trend over last N months"""
        qs = self.get_transactions_queryset()
        
        trend_data = []
        today = date.today()
        
        for i in range(months - 1, -1, -1):
            month_date = today - timedelta(days=30 * i)
            month_start = date(month_date.year, month_date.month, 1)
            
            if month_date.month == 12:
                month_end = date(month_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(month_date.year, month_date.month + 1, 1) - timedelta(days=1)
            
            month_qs = qs.filter(date__gte=month_start, date__lte=month_end)
            
            income = month_qs.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
            expenses = month_qs.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
            
            trend_data.append({
                'month': f'{month_start.year}-{month_start.month:02d}',
                'income': float(income),
                'expenses': float(expenses),
            })
        
        return {'trend': trend_data}
