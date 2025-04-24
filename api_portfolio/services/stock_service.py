from api_portfolio.models import Stock, StockPrice

class StockService:
    @staticmethod
    def get_current_price(stock):
        return stock.prices.latest('date').price

    @staticmethod
    def get_or_create_stock(symbol, defaults=None):
        return Stock.objects.get_or_create(
            symbol=symbol.upper(),
            defaults=defaults or {}
        )
