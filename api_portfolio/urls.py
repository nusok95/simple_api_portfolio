"""
URL configuration for api_portfolio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import AddStocksToPortfolioView, CreatePortfolioView, PortfolioListView, PortfolioSummaryView, StockListView, StockCreateView, StockPricesView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/stocks/', StockListView.as_view(), name='stock-list'),
    path('api/stocks/create', StockCreateView.as_view(), name='stock-create'),
    path('api/portfolios/create', CreatePortfolioView.as_view(), name='create-portfolio'),
    path('api/portfolios', PortfolioListView.as_view(), name='list-portfolio'),
    path('api/stocks/prices/<str:symbol>/', StockPricesView.as_view(), name='stock-prices'),
    path('api/portfolios/<str:name>/add_stocks/', AddStocksToPortfolioView.as_view(), name='add-stocks-to-portfolio'),
    path('api/portfolios/<str:name>/summary/', PortfolioSummaryView.as_view(), name='portfolio-summary'),
]
