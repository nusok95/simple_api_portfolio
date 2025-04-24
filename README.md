# Simple Portfolio API

This is an simple portfolio API developed with Django and Django Rest Framework. 

You can create portfolios, see the stocks, their prices in the time and add stocks to your portfolio, also you can see the summary of your portfolio between dates data like profit and annualized return is included. 

Currently working on transferring profits to bank accounts 😈

## Development Setup

1. Install dependencies:
```bash
cd api_portfolio
pip install -r requirements.txt
```

2. Create the database migrations:
```bash
python manage.py makemigrations
```

3. Apply migrations:
```bash
python manage.py migrate
```

4. Create fake Stocks (optional):
```bash
python manage.py generate_fake_stocks
# Create new stocks (default)
python manage.py generate_fake_stocks --stocks=5 --days=30

# Update existing stocks' prices
python manage.py generate_fake_stocks --days=30 --update

# Custom prefix
python manage.py generate_fake_stocks --prefix=MYSTK --stocks=3 --days=10
```

5. Run development server:
```bash
python manage.py runserver
```

6. Begin to invest :1313:
```
http://localhost:8000/api/
```

## Base URL
`http://localhost:8000/api/`

## Authentication
No authentication required for development.

---

## Stock Endpoints

### List All Stocks
`GET /stocks/`

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "symbol": "AAPL",
        "name": "Apple Inc."
    }
]
```

---

### Create Stock
`POST /stocks/create`

**Request (form-data):**
- `name`: "Apple Inc."
- `symbol`: "AAPL"

**Response (201 Created):**
```json
{
    "id": 1,
    "symbol": "AAPL",
    "name": "Apple Inc."
}
```

---

### Get Stock Prices
`GET /stocks/prices/{symbol}/`

**Response (200 OK):**
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/stocks/prices/AAPL/?page=2",
    "previous": null,
    "results": [
        {
            "date": "2025-04-25",
            "price": "150.05",
            "volume": 5000000
        }
    ]
}
```

---

## Portfolio Endpoints

### Create Portfolio
`POST /portfolios/create`

**Request:**
```json
{
    "name": "portfolio_name",
    "stocks": [
        {
            "symbol": "AAPL",
            "quantity": 10
        }
    ]
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "name": "portfolio_name",
    "created_at": "2025-04-25T12:00:00Z"
}
```

---

### Add Stocks to Portfolio
`POST /portfolios/{portfolio_name}/add_stocks/`

**Request:**
```json
{
    "stocks": [
        {
            "symbol": "MSFT",
            "quantity": 5
        }
    ]
}
```

**Response (200 OK):**
```json
{
    "portfolio": "portfolio_name",
    "created_holdings": 1,
    "updated_holdings": 0,
    "total_holdings": 1,
    "current_value": 1500.50
}
```

---

### List All Portfolios
`GET /portfolios/`

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "portfolio_name",
        "created_at": "2025-04-25T12:00:00Z",
        "total_value": 1500.50,
        "total_profit": 50.25,
        "annualized_return": 5.933557837420283,
        "stocks": [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "quantity": "10.00",
                "current_price": 150.05,
                "profit": 50.25
            }
        ]
    }
]
```

---

### Get Portfolio Summary
`GET /portfolios/{portfolio_name}/summary`

**Query Parameters:**
- `start_date` (optional): Filter start date (YYYY-MM-DD)
- `end_date` (optional): Filter end date (YYYY-MM-DD)

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "portfolio_name",
    "created_at": "2025-04-25T12:00:00Z",
    "total_value": 1500.50,
    "total_profit": 50.25,
    "stocks": [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "quantity": "10.00",
            "current_price": 150.05,
            "profit": 50.25
        }
    ]
}
```

---



## Error Responses

### 400 Bad Request
```json
{
    "error": "Invalid input data",
    "details": {
        "field_name": ["Error message"]
    }
}
```

### 404 Not Found
```json
{
    "detail": "Not found"
}
```

### 500 Server Error
```json
{
    "error": "Internal server error"
}
```

---

## Examples

### Create a new portfolio with stocks:
```bash
curl -X POST "http://localhost:8000/api/portfolios/create" \
-H "Content-Type: application/json" \
-d '{"name": "tech", "stocks": [{"symbol": "AAPL", "quantity": 10}]}'
```

### Get portfolio summary with date range:
```bash
curl "http://localhost:8000/api/portfolios/tech/summary?start_date=2025-04-01&end_date=2025-04-25"
```

### Add new stocks to existing portfolio:
```bash
curl -X POST "http://localhost:8000/api/portfolios/tech/add_stocks/" \
-H "Content-Type: application/json" \
-d '{"stocks": [{"symbol": "MSFT", "quantity": 5}]}'
```