from decimal import Decimal
from api_portfolio.utils.constants import (
    YEAR_DAYS,
    ZERO_ANNUALIZED_RETURN,
    ZERO_INVESTMENT,
    ZERO_YEARS
    )
from api_portfolio.models import StockPrice

class ProfitCalculator:
    @staticmethod
    def calculate_profit(queryset, start_date, end_date, quantity=1):
        try:
            start_price = queryset.filter(date__lte=start_date).latest('date').price
            end_price = queryset.filter(date__lte=end_date).latest('date').price
            return (Decimal(end_price) - Decimal(start_price)) * Decimal(quantity)
        except StockPrice.DoesNotExist:
            return None

    @classmethod
    def portfolio_profit(cls, portfolio, start_date, end_date):
        total = Decimal('0')
        for holding in portfolio.holdings.all():
            profit = cls.calculate_profit(
                holding.stock.prices,
                start_date,
                end_date,
                holding.quantity
            )
            if profit is not None:
                total += profit
        return total
    
    @classmethod
    def _get_initial_investment(cls, portfolio, start_date):
        total = Decimal('0')
        for holding in portfolio.holdings.all():
            try:
                price = holding.stock.prices.filter(
                    date__lte=start_date
                ).latest('date').price
                total += Decimal(price) * Decimal(holding.quantity)
            except StockPrice.DoesNotExist:
                continue
        return total

    @classmethod
    def annualized_return(cls, portfolio, start_date, end_date):
        total_profit = cls.portfolio_profit(portfolio, start_date, end_date)
        initial_investment = cls._get_initial_investment(portfolio, start_date)

        if initial_investment == ZERO_INVESTMENT:
            return ZERO_ANNUALIZED_RETURN

        try:
            years = (end_date - start_date).days / YEAR_DAYS
            
            if years <= ZERO_YEARS:
                return ZERO_ANNUALIZED_RETURN
            
            initial_investment = Decimal(str(initial_investment))
            years = Decimal(str(years))
        
            return float((1 + (total_profit / initial_investment)) ** (1 / years) - 1)
        except (ValueError, TypeError):
            return ZERO_ANNUALIZED_RETURN
