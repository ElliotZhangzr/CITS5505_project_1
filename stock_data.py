from models import Stock, StockPrice


def get_stock_data(limit=400):
    stocks = Stock.query.order_by(Stock.symbol).all()
    market_data = {}

    for stock in stocks:
        prices = (
            StockPrice.query
            .filter_by(stock_id=stock.id)
            .order_by(StockPrice.recorded_at.desc(), StockPrice.id.desc())
            .limit(limit)
            .all()
        )
        market_data[stock.symbol] = [float(item.price) for item in reversed(prices)]  # reversed: DB returns newest-first, chart needs chronological order

    return {
        "stocks": [
            {
                "id": stock.id,
                "symbol": stock.symbol,
                "name": stock.name,
                "volatility": float(stock.volatility),
                "liquidity": float(stock.liquidity),
                "tradeImpactFactor": float(stock.trade_impact_factor),
            }
            for stock in stocks
        ],
        "marketData": market_data,
    }
