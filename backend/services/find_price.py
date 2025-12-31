import yfinance as yf

def get_current_price(ticker: str) -> float:
    """
    yfinance를 이용해 현재가를 가져옵니다.
    """
    try:
        stock = yf.Ticker(ticker)
        # fast_info가 가장 빠르고 부하가 적습니다.
        price = stock.fast_info.last_price
        return price
    except Exception as e:
        print(f"⚠️ [Price] yfinance Error ({ticker}): {e}")
        return 0.0