"""Views for Analytics app"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.analytics.services import AnalyticsService
from apps.users.permissions import IsAnalystOrAdmin
from utils.csv_export import export_analytics_to_csv


class AnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for analytics endpoints"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get financial summary"""
        service = AnalyticsService(request.user)
        data = service.get_summary()
        
        return Response(
            {
                'error': False,
                'data': data,
            },
            status=status.HTTP_200_OK,
        )
    
    @action(detail=False, methods=['get'])
    def category_breakdown(self, request):
        """Get category breakdown"""
        service = AnalyticsService(request.user)
        data = service.get_category_breakdown()
        
        return Response(
            {
                'error': False,
                'data': data,
            },
            status=status.HTTP_200_OK,
        )
    
    @action(detail=False, methods=['get'])
    def monthly_totals(self, request):
        """Get monthly totals"""
        year = request.query_params.get('year')
        
        service = AnalyticsService(request.user)
        data = service.get_monthly_totals(year=int(year) if year else None)
        
        return Response(
            {
                'error': False,
                'data': data,
            },
            status=status.HTTP_200_OK,
        )
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Get recent activity"""
        limit = request.query_params.get('limit', 10)
        
        try:
            limit = int(limit)
            if limit < 1 or limit > 100:
                limit = 10
        except ValueError:
            limit = 10
        
        service = AnalyticsService(request.user)
        data = service.get_recent_activity(limit=limit)
        
        return Response(
            {
                'error': False,
                'data': data,
            },
            status=status.HTTP_200_OK,
        )
    
    @action(detail=False, methods=['get'])
    def category_totals(self, request):
        """Get totals by category"""
        transaction_type = request.query_params.get('type')
        
        service = AnalyticsService(request.user)
        data = service.get_category_totals(transaction_type=transaction_type)
        
        return Response(
            {
                'error': False,
                'data': {'category_totals': data},
            },
            status=status.HTTP_200_OK,
        )
    
    @action(detail=False, methods=['get'])
    def spending_trend(self, request):
        """Get spending trend"""
        months = request.query_params.get('months', 6)
        
        try:
            months = int(months)
            if months < 1 or months > 24:
                months = 6
        except ValueError:
            months = 6
        
        service = AnalyticsService(request.user)
        data = service.get_spending_trend(months=months)
        
        return Response(
            {
                'error': False,
                'data': data,
            },
            status=status.HTTP_200_OK,
        )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAnalystOrAdmin])
    def export_csv(self, request):
        """Export analytics to CSV"""
        service = AnalyticsService(request.user)
        
        analytics_data = {
            'total_income': service.get_summary()['total_income'],
            'total_expenses': service.get_summary()['total_expenses'],
            'current_balance': service.get_summary()['current_balance'],
            **service.get_category_breakdown(),
        }
        
        return export_analytics_to_csv(analytics_data)
