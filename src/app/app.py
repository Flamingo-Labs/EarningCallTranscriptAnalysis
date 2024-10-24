from flask import Flask, request, render_template
import os
import getpass
import sys

# Add FinanceFetch_Cdahlback to sys.path
financefetch_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'FinanceFetch_Cdahlback'))
sys.path.append(financefetch_path)

# Add GPTWrapper to sys.path
gptwrapper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'GPTWrapper'))
sys.path.append(gptwrapper_path)

from stock_data_fetcher import StockDataFetcher, plot_candle_interactive
from constants import APIKEY
from text_summarizer import TextSummarizer

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    if file:
        # Read the file content
        text_content = file.read().decode('utf-8')

        # Initialize the TextSummarizer with the API key (optional) and without a file path
        summarizer = TextSummarizer(api_key=APIKEY)
        
        # Set the loaded content manually from the uploaded file
        summarizer.text_content = text_content
        
        # Summarize the text
        summarizer.summarize_text()
        
        # Return the summary to the frontend
        summary = summarizer.summary  # Extract the generated summary
        return render_template('index.html', summary=summary)
    

@app.route('/view_stock', methods=['POST'])
def view_stock():
    # Assume you have logic here to get stock data as a DataFrame
    symbol = request.form['symbol']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    
    stock_fetcher = StockDataFetcher(symbol)
    historical_data = stock_fetcher.fetch_historical_data(period="1y", interval="1d")

    # Filter data for the provided date range
    filtered_data = historical_data[start_date:end_date]

    # Prepare chart data
    stock_chart = plot_candle_interactive(filtered_data)
    # print(stock_chart)  # Add this line for debugging
    return render_template('index.html', stock_chart=stock_chart, symbol=symbol)


# Stock chart viewing route
# @app.route('/view_stock', methods=['POST'])
# def view_stock():
#     symbol = request.form['symbol']
#     start_date = request.form['start_date']
#     end_date = request.form['end_date']

#     stock_fetcher = StockDataFetcher(symbol)
#     historical_data = stock_fetcher.fetch_historical_data(period="1y", interval="1d")

#     # Filter data for the provided date range
#     filtered_data = historical_data[start_date:end_date]

#     # Generate stock chart data
#     stock_chart = plot_candle_interactive(filtered_data)

#     return render_template('index.html', stock_chart=stock_chart, symbol=symbol)


if __name__ == '__main__':
    app.run(debug=True)
