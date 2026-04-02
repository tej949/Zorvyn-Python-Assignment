"""
CSV export utilities for Finance System Backend
"""
import csv
from io import StringIO
from django.http import HttpResponse
from decimal import Decimal


def export_transactions_to_csv(transactions):
    """
    Export transactions to CSV format
    
    Args:
        transactions: QuerySet or list of Transaction objects
    
    Returns:
        HttpResponse with CSV file
    """
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID',
        'Amount',
        'Type',
        'Category',
        'Date',
        'Description',
        'Created At',
        'Updated At',
    ])
    
    # Write data rows
    for transaction in transactions:
        writer.writerow([
            transaction.id,
            str(transaction.amount),
            transaction.type,
            transaction.category,
            transaction.date.strftime('%Y-%m-%d') if transaction.date else '',
            transaction.description or '',
            transaction.created_at.isoformat() if transaction.created_at else '',
            transaction.updated_at.isoformat() if transaction.updated_at else '',
        ])
    
    # Create HTTP response
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    
    return response


def export_analytics_to_csv(analytics_data):
    """
    Export analytics summary to CSV format
    
    Args:
        analytics_data: Dictionary with analytics data
    
    Returns:
        HttpResponse with CSV file
    """
    output = StringIO()
    writer = csv.writer(output)
    
    # Write summary section
    writer.writerow(['Financial Summary'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Income', str(analytics_data.get('total_income', 0))])
    writer.writerow(['Total Expenses', str(analytics_data.get('total_expenses', 0))])
    writer.writerow(['Current Balance', str(analytics_data.get('current_balance', 0))])
    writer.writerow([])
    
    # Write category breakdown
    writer.writerow(['Income by Category'])
    writer.writerow(['Category', 'Amount'])
    for category, amount in analytics_data.get('income_by_category', {}).items():
        writer.writerow([category, str(amount)])
    writer.writerow([])
    
    writer.writerow(['Expenses by Category'])
    writer.writerow(['Category', 'Amount'])
    for category, amount in analytics_data.get('expense_by_category', {}).items():
        writer.writerow([category, str(amount)])
    
    # Create HTTP response
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="analytics.csv"'
    
    return response


def export_audit_logs_to_csv(audit_logs):
    """
    Export audit logs to CSV format
    
    Args:
        audit_logs: QuerySet or list of AuditLog objects
    
    Returns:
        HttpResponse with CSV file
    """
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID',
        'User ID',
        'Action',
        'Model',
        'Object ID',
        'Changes',
        'Timestamp',
    ])
    
    # Write data rows
    for log in audit_logs:
        writer.writerow([
            log.id,
            log.user_id,
            log.action,
            log.model,
            log.object_id,
            str(log.changes),
            log.timestamp.isoformat() if log.timestamp else '',
        ])
    
    # Create HTTP response
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
    
    return response
