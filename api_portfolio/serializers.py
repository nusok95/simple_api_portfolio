from rest_framework import serializers
from api_portfolio.models import Stock, Portfolio, Holding, StockPrice
from api_portfolio.services.stock_service import StockService
from api_portfolio.services.portfolio_service import PortfolioService
from api_portfolio.services.profit_calculator import ProfitCalculator
from api_portfolio.utils.constants import (
    MAX_LENGTH_SYMBOL,
    MAX_LENGTH_QUANTITY,
    MAX_LENGTH_QUANTITY_DECIMAL_PLACES,
    ZERO_PROFIT
)
from api_portfolio.utils.mixins import DateValidationMixin


class SimpleStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name']
        read_only_fields = ['id']

class StockPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPrice
        fields = ['date', 'price']

class HoldingSerializer(serializers.ModelSerializer):
    stock = SimpleStockSerializer()
    
    class Meta:
        model = Holding
        fields = ['id', 'stock', 'quantity', 'purchase_date']
        read_only_fields = ['id']

class PortfolioStockSerializer(serializers.Serializer):
    symbol = serializers.CharField(source='stock.symbol')
    name = serializers.CharField(source='stock.name')
    quantity = serializers.DecimalField(
        max_digits=MAX_LENGTH_QUANTITY,
        decimal_places=MAX_LENGTH_QUANTITY_DECIMAL_PLACES
        )
    current_price = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()

    def get_current_price(self, obj):
        return StockService.get_current_price(obj.stock)

    def get_profit(self, obj):
        request = self.context.get('request')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return None
            
        return ProfitCalculator.calculate_profit(
            obj.stock.prices,
            start_date,
            end_date,
            obj.quantity
        )

class PortfolioSummarySerializer(DateValidationMixin, serializers.ModelSerializer):
    stocks = PortfolioStockSerializer(many=True, source='holdings')
    total_value = serializers.SerializerMethodField()
    total_profit = serializers.SerializerMethodField()
    annualized_return = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'created_at', 'total_value', 'total_profit', 'annualized_return','stocks']
        read_only_fields = fields

    def get_total_value(self, portfolio):
        portfolio_service = PortfolioService(portfolio)
        return portfolio_service.calculate_total_value()

    def get_total_profit(self, portfolio):
        request = self.context.get('request')
        start_date = self.validate_dates(request.query_params.get('start_date'))
        end_date = self.validate_dates(request.query_params.get('end_date'))
        
        if not start_date or not end_date:
            return ZERO_PROFIT
            
        return ProfitCalculator.portfolio_profit(portfolio, start_date, end_date)
    
    def get_annualized_return(self, portfolio):
        request = self.context.get('request')
        start_date = self.validate_dates(request.query_params.get('start_date'))
        end_date = self.validate_dates(request.query_params.get('end_date'))
        
        if not start_date or not end_date:
            return ZERO_PROFIT
            
        return ProfitCalculator.annualized_return(portfolio, start_date, end_date)

class PortfolioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['id', 'name']
        read_only_fields = ['id']

class AddStockSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=MAX_LENGTH_SYMBOL)
    quantity = serializers.DecimalField(
        max_digits=MAX_LENGTH_QUANTITY,
        decimal_places=MAX_LENGTH_QUANTITY_DECIMAL_PLACES
        )
    purchase_date = serializers.DateField(required=False)

class AddStocksToPortfolioSerializer(serializers.Serializer):
    stocks = AddStockSerializer(many=True)
