import yfinance as yf
import pandas as pd
import mplfinance as mpf
import plotly.graph_objects as go

class StockDataFetcher:
    def __init__(self, symbol: str):
        """
        Initializes the StockDataFetcher with a stock symbol.
        :param symbol: Stock ticker symbol (e.g., 'AAPL').
        """
        self.symbol = symbol
    
    def fetch_historical_data(self, csv_path: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetches historical stock data for the provided symbol and saves it to a CSV file.
        
        :param csv_path: The file path where the CSV will be saved.
        :param period: Time period of the historical data (e.g., '1y', '5d', '1mo', etc.).
        :param interval: Data interval (e.g., '1d' for daily, '1h' for hourly).
        :return: A DataFrame with historical data for the stock, including earnings report information.
        """
        stock = yf.Ticker(self.symbol)
        df = stock.history(period=period, interval=interval)

        # Fetch earnings report dates
        earnings_df = stock.earnings_dates

        # Ensure both DataFrame 'Date' columns are in the same format and timezone
        earnings_df.index = pd.to_datetime(earnings_df.index).normalize()  # Normalize to remove time components
        df.index = pd.to_datetime(df.index).normalize()  # Normalize the dates

        # Add 'HasEarningsReport' column, marking True for dates with earnings reports
        df['HasEarningsReport'] = df.index.isin(earnings_df.index)

        # Localize the index to the appropriate timezone if it is not already tz-aware
        if df.index.tz is None:
            df.index = df.index.tz_localize('America/New_York')

        return df
    
    def save_historical_data(self, data: pd.DataFrame, csv_path: str) -> None:
        """
        Saves historical stock data to a CSV file.
        
        :param data: A DataFrame containing historical stock data.
        :param csv_path: The file path where the CSV will be saved.
        """
        data.to_csv(csv_path)
    
    def load_historical_data(self, csv_path: str) -> pd.DataFrame:
        """
        Loads historical stock data from a saved CSV file.
        
        :param csv_path: The file path of the CSV to load.
        :return: A DataFrame with historical stock data.
        """
        # Load the CSV into a DataFrame
        df = pd.read_csv(csv_path, parse_dates=['Date'], index_col='Date')
        
        # Ensure the index is a datetime index
        df.index = pd.to_datetime(df.index, utc=True)  # Convert to UTC-aware datetime
        
        # Convert the index to the desired timezone
        df.index = df.index.tz_convert('America/New_York')  # Convert to local timezone if needed
        
        return df
        
    def get_real_time_price(self) -> pd.DataFrame:
        """
        Fetches the real-time stock price for the symbol.
        :return: A DataFrame containing the real-time price and additional info for the stock.
        """
        stock = yf.Ticker(self.symbol)
        price_info = stock.history(period='1d')
        if not price_info.empty:
            latest_price = price_info['Close'].iloc[-1]
            return pd.DataFrame([{'Symbol': self.symbol, 'Price': latest_price}])
        return pd.DataFrame()

    def get_metadata(self) -> pd.DataFrame:
        """
        Fetches metadata (e.g., market cap, sector) for the stock symbol.
        :return: A DataFrame containing metadata for the stock.
        """
        stock = yf.Ticker(self.symbol)
        info = stock.info
        metadata = {
            'Symbol': self.symbol,
            'Company Name': info.get('shortName'),
            'Market Cap': info.get('marketCap'),
            'Sector': info.get('sector'),
            'Industry': info.get('industry'),
        }
        return pd.DataFrame([metadata])
    

def plot_candle_interactive(data, start_date=None, end_date=None):
    """
    Plots an interactive candlestick chart with hover information.
    
    :param data: A DataFrame containing historical stock data.
    :param start_date: The start date for filtering the data (inclusive).
    :param end_date: The end date for filtering the data (inclusive).
    """
    # Ensure the 'Date' column is the index (since you're using index as Date)
    data['Date'] = data.index  # Make sure index is used as 'Date'

    # Convert the start_date and end_date to the same timezone as data's Date column
    if start_date:
        start_date = pd.to_datetime(start_date).tz_localize(data['Date'].dt.tz)
    if end_date:
        end_date = pd.to_datetime(end_date).tz_localize(data['Date'].dt.tz)

    # Filter data for the specified date range
    if start_date:
        data = data[data['Date'] >= start_date]
    if end_date:
        data = data[data['Date'] <= end_date]
    
    # Calculate percent change
    data['Percent Change'] = (data['Close'] - data['Open']) / data['Open'] * 100

    # Create the candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=data['Date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        hovertext=[
            f"Open: {row['Open']}<br>Close: {row['Close']}<br>Percent Change: {row['Percent Change']:.2f}%<br>Date: {row['Date']}"
            for _, row in data.iterrows()
        ],
        hoverinfo="text"
    )])

    # Add markers for earnings report days
    earnings_dates = data[data['HasEarningsReport'] == True]

    fig.add_trace(go.Scatter(
        x=earnings_dates['Date'],
        y=earnings_dates['Close'],
        mode='markers',
        marker=dict(symbol='triangle-up', size=25, color='red'),
        name="Earnings Report Day",
        hovertext=[
            f"Earnings Report Day<br>Close: {row['Close']}" for _, row in earnings_dates.iterrows()
        ],
        hoverinfo="text"
    ))

    # Update layout
    fig.update_layout(
        title='Candlestick Chart with Earnings Report Days',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False
    )
    
    # Show the figure
    fig.show()


if __name__ == "__main__":
    # Example usage:
    # Initialize the fetcher with a single stock symbol
    stock_fetcher = StockDataFetcher('AAPL')

    # Fetch historical data (past 1 year, daily interval) and save it to a csv
    # historical_data = stock_fetcher.save_historical_data(csv_path="AAPL_historical_data.csv", period="1y", interval="1d")
    historical_data = stock_fetcher.load_historical_data("AAPL_historical_data.csv")
    print(historical_data)

    # Fetch real-time stock price
    real_time_price = stock_fetcher.get_real_time_price()
    print(real_time_price)  # Display real-time price for AAPL

    # Fetch metadata for the company
    metadata = stock_fetcher.get_metadata()
    print(metadata)  # Display metadata for AAPL

    # Plot candlestick chart using the historical data
    plot_candle_interactive(historical_data, start_date='2024-01-01', end_date='2024-10-01')