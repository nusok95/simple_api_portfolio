import random
import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from api_portfolio.models import Stock, StockPrice
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generates fake stocks with realistic price history'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=40,
            help='Number of historical days to generate'
        )
        parser.add_argument(
            '--stocks',
            type=int,
            default=10,
            help='Number of stocks to create'
        )
        parser.add_argument(
            '--prefix',
            type=str,
            default='STK',
            help='Prefix for stock symbols'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing stocks instead of creating new ones'
        )

    def handle(self, *args, **options):
        if options['update']:
            self.update_stock_prices(options['days'], options['prefix'])
        else:
            self.generate_stocks(options['stocks'], options['days'], options['prefix'])
        self.stdout.write(
            self.style.SUCCESS(
                f"Processed stocks with {options['days']} days of price history"
            )
        )

    def generate_unique_symbol(self, prefix='STK'):
        max_attempts = 10
        for _ in range(max_attempts):
            timestamp_part = str(int(time.time()))[-6:]
            random_part = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))
            symbol = f"{prefix}{timestamp_part}{random_part}"[:10]
            
            if not Stock.objects.filter(symbol=symbol).exists():
                return symbol
        raise ValueError("Could not generate unique stock symbol")

    def generate_stocks(self, num_stocks, num_days, prefix):
        stocks = []
        existing_symbols = set(Stock.objects.values_list('symbol', flat=True))

        for _ in range(num_stocks):
            symbol = self.generate_unique_symbol(prefix)
            while symbol in existing_symbols:
                symbol = self.generate_unique_symbol(prefix)
            existing_symbols.add(symbol)
            
            stocks.append(Stock(
                symbol=symbol,
                name=f"Fake Stock {symbol}",
                description=f"Test stock {symbol} for portfolio simulation"
            ))
        
        try:
            Stock.objects.bulk_create(stocks)
            self.generate_prices(num_days, list(existing_symbols))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating stocks: {e}"))

    def update_stock_prices(self, num_days, prefix):
        symbols = Stock.objects.filter(symbol__startswith=prefix).values_list('symbol', flat=True)
        self.generate_prices(num_days, symbols)

    def generate_prices(self, num_days, symbols):
        today = timezone.now().date()
        price_records = []
        
        for stock in Stock.objects.filter(symbol__in=symbols):
            existing_dates = set(StockPrice.objects.filter(
                stock=stock
            ).values_list('date', flat=True))
            
            try:
                latest_price = StockPrice.objects.filter(
                    stock=stock
                ).latest('date').price
            except StockPrice.DoesNotExist:
                latest_price = random.uniform(10, 200)
            
            volatility = random.uniform(0.005, 0.03)
            
            for days_ago in range(num_days, -1, -1):
                date = today - timedelta(days=days_ago)
                
                if date in existing_dates:
                    continue
                
                if days_ago == num_days:
                    price = latest_price * random.uniform(0.9, 1.1)
                else:
                    change_percent = random.gauss(0, volatility)
                    price = price_records[-1].price * (1 + change_percent)
                
                price_records.append(StockPrice(
                    stock=stock,
                    date=date,
                    price=round(price, 2),
                ))
        
        try:
            batch_size = 1000
            for i in range(0, len(price_records), batch_size):
                StockPrice.objects.bulk_create(price_records[i:i + batch_size])
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating prices: {e}"))
