from decimal import Decimal
from django.utils import timezone
from api_portfolio.models import Holding
from api_portfolio.services.stock_service import StockService

class PortfolioService:
    def __init__(self, portfolio):
        self.portfolio = portfolio

    def calculate_total_value(self):
        total = Decimal('0')
        for holding in self.portfolio.holdings.all():
            price = StockService.get_current_price(holding.stock)
            total += Decimal(price) * Decimal(holding.quantity)
        return total

    def add_stocks_to_portfolio(self, stocks_data):
        created = 0
        updated = 0
        
        for stock_data in stocks_data:
            symbol = stock_data['symbol'].upper()
            quantity = Decimal(stock_data['quantity'])
            purchase_date = stock_data.get('purchase_date', timezone.now().date())
            
            stock, _ = StockService.get_or_create_stock(symbol)
            
            holding, is_created = Holding.objects.get_or_create(
                portfolio=self.portfolio,
                stock=stock,
                defaults={
                    'quantity': quantity,
                    'purchase_date': purchase_date
                }
            )
            
            if not is_created:
                holding.quantity += quantity
                if purchase_date < holding.purchase_date:
                    holding.purchase_date = purchase_date
                holding.save()
                updated += 1
            else:
                created += 1
                
        return created, updated
