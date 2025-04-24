from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from api_portfolio.models import Stock, Portfolio, StockPrice
from api_portfolio.serializers import (
    AddStocksToPortfolioSerializer,
    PortfolioCreateSerializer,
    PortfolioSummarySerializer,
    SimpleStockSerializer,
    StockPriceSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from api_portfolio.services.portfolio_service import PortfolioService 


class PortfolioListView(generics.ListAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSummarySerializer


class StockListView(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = SimpleStockSerializer


class StockCreateView(generics.CreateAPIView):
    queryset = Stock.objects.all()
    serializer_class = SimpleStockSerializer


class CreatePortfolioView(generics.CreateAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        portfolio = serializer.save()
        
        response_data = {
            'id': portfolio.id,
            'name': portfolio.name,
            'created_at': portfolio.created_at,
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class AddStocksToPortfolioView(generics.GenericAPIView):
    serializer_class = AddStocksToPortfolioSerializer

    def post(self, request, name, *args, **kwargs):
        portfolio = get_object_or_404(Portfolio, name=name)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        portfolio_service = PortfolioService(portfolio)
        created_count, updated_count = portfolio_service.add_stocks_to_portfolio(
            serializer.validated_data['stocks']
        )

        response_data = {
            'portfolio': portfolio.name,
            'created_holdings': created_count,
            'updated_holdings': updated_count,
            'total_holdings': portfolio.holdings.count(),
            'current_value': portfolio_service.calculate_total_value()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class StockPricesView(APIView):
    pagination_class = StandardResultsSetPagination
    
    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            self._paginator = self.pagination_class()
        return self._paginator
    
    def paginate_queryset(self, queryset):
        return self.paginator.paginate_queryset(queryset, self.request, view=self)
    
    def get(self, request, symbol, format=None):
        stock = get_object_or_404(Stock, symbol=symbol.upper())
        
        prices = StockPrice.objects.filter(stock=stock).order_by('-date')
        
        page = self.paginate_queryset(prices)
        
        if page is not None:
            serializer = StockPriceSerializer(page, many=True)
            return self.paginator.get_paginated_response(serializer.data)
        
        serializer = StockPriceSerializer(prices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PortfolioSummaryView(generics.RetrieveAPIView):
    serializer_class = PortfolioSummarySerializer
    lookup_field = 'name'
    lookup_url_kwarg = 'name'

    def get(self, request, name, *args, **kwargs):
        portfolio = get_object_or_404(Portfolio, name=name)
        serializer = self.get_serializer(portfolio, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)
