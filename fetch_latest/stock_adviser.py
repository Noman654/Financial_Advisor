import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import vertexai
from vertexai.preview.generative_models import GenerativeModel, ChatSession

# # 1. Get Stock Information (Full Year)
# stock_name = 'TATAMOTORS.NS'  




def get_stocks_data(stock_code: str):
    stock = yf.Ticker(stock_code)
    fundamentals = stock.info  # Dictionary containing fundamental data

    # Example: Print the 'marketCap' (market capitalization)
    # print(f"Market Cap: {fundamentals['marketCap']}")
    mandotary_columns = ['longBusinessSummary', 'auditRisk', 'boardRisk', 'compensationRisk', 'shareHolderRightsRisk', 'overallRisk', 'governanceEpochDate', 'compensationAsOfEpochDate', 'maxAge', 'priceHint', 'previousClose', 'open', 'dayLow', 'dayHigh', 'regularMarketPreviousClose', 'regularMarketOpen', 'regularMarketDayLow', 'regularMarketDayHigh', 'dividendRate', 'dividendYield', 'exDividendDate', 'payoutRatio', 'fiveYearAvgDividendYield', 'beta', 'trailingPE', 'forwardPE', 'volume', 'regularMarketVolume', 'averageVolume', 'averageVolume10days', 'averageDailyVolume10Day', 'ask', 'marketCap', 'fiftyTwoWeekLow', 'fiftyTwoWeekHigh', 'priceToSalesTrailing12Months', 'fiftyDayAverage', 'twoHundredDayAverage', 'trailingAnnualDividendRate', 'trailingAnnualDividendYield', 'currency', 'enterpriseValue', 'profitMargins', 'floatShares', 'sharesOutstanding', 'heldPercentInsiders', 'heldPercentInstitutions', 'impliedSharesOutstanding', 'bookValue', 'priceToBook', 'lastFiscalYearEnd', 'nextFiscalYearEnd', 'mostRecentQuarter', 'earningsQuarterlyGrowth', 'netIncomeToCommon', 'trailingEps', 'forwardEps', 'lastSplitFactor', 'lastSplitDate', 'enterpriseToRevenue', 'enterpriseToEbitda', '52WeekChange', 'SandP52WeekChange', 'lastDividendValue', 'lastDividendDate', 'exchange', 'quoteType', 'symbol', 'underlyingSymbol', 'shortName', 'longName', 'firstTradeDateEpochUtc', 'timeZoneFullName', 'timeZoneShortName', 'uuid', 'messageBoardId', 'gmtOffSetMilliseconds', 'currentPrice', 'targetHighPrice', 'targetLowPrice', 'targetMeanPrice', 'targetMedianPrice', 'recommendationMean', 'recommendationKey', 'numberOfAnalystOpinions', 'totalCash', 'totalCashPerShare', 'ebitda', 'totalDebt', 'quickRatio', 'currentRatio', 'totalRevenue', 'debtToEquity', 'revenuePerShare', 'returnOnAssets', 'returnOnEquity', 'freeCashflow', 'operatingCashflow', 'earningsGrowth', 'revenueGrowth', 'grossMargins', 'ebitdaMargins', 'operatingMargins', 'financialCurrency', 'trailingPegRatio']

    fundamentals_data = {}
    for colum in mandotary_columns:
        fundamentals_data[colum] = fundamentals.get(colum)

    finacial_data = stock.quarterly_financials.iloc[:, :3].to_dict()
    
    return {'finacial_data':finacial_data, 'fundamentals_data':fundamentals_data}


def get_chat_response(chat: ChatSession, prompt: str):
    response = chat.send_message(prompt)
    return response.text

def generate_investment_suggestion(fundamental_data, quarterly_results_data, chat, news_titles):
    """
    Generates an investment suggestion based on fundamental and quarterly results data.

    Args:
        fundamental_data (dict): Dictionary containing fundamental data points.
        quarterly_results_data (dict): Dictionary containing quarterly results data.

    Returns:
        str: Investment suggestion.
    """

    prompt = f"""
    Analyze the following fundamental and quarterly results data for a stock:

    Fundamental Data:
    {fundamental_data}

    Quarterly Results:
    {quarterly_results_data}

    News Titles:
    {news_titles}

    For each news headline, describe its potential impact in one line, including the source, link, and timing.
    Provide a concise investment suggestion (Buy, Hold, Sell) and a brief justification based on the analysis of fundamental results and news and show the precentange and nummber if possible.

    This analysis should help in making an informed investment decision by considering both financial performance and recent market sentiment.

     """
     # or other appropriate model
    response = get_chat_response(chat,
        prompt
    )

    return response





def get_trend(stock_name: str):
    df_full_year = yf.download(stock_name, period='1y') 


    # 2. Calculate Important Signals for the Full Year
    # Smooth out the price changes to see overall trends
    df_full_year['ShortTermTrend'] = df_full_year['Close'].rolling(window=20).mean()
    df_full_year['LongTermTrend'] = df_full_year['Close'].rolling(window=50).mean()

    # Measure how quickly the price is changing
    df_full_year['PriceChangeSpeed'] = 100 - (100 / (1 + (df_full_year['Close'].diff().where(df_full_year['Close'].diff() > 0, 0)).rolling(window=14).mean() / (-df_full_year['Close'].diff().where(df_full_year['Close'].diff() < 0, 0)).rolling(window=14).mean()))

    # 3. Figure Out When to Buy or Sell for the Full Year
    df_full_year['Action'] = 'Hold'  
    df_full_year.loc[df_full_year['ShortTermTrend'] > df_full_year['LongTermTrend'], 'Action'] = 'Buy' 
    df_full_year.loc[df_full_year['ShortTermTrend'] < df_full_year['LongTermTrend'], 'Action'] = 'Sell' 

    # 4. Filter for the Last 3 Months
    end_date = datetime.today()
    start_date = end_date - timedelta(days=90)
    df = df_full_year.loc[start_date:end_date].copy()  # Get only the last 3 months of data

    # 5. Create a Picture of the Stock's Performance (Last 3 Months)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, 
                        row_heights=[0.7, 0.3], specs=[[{"secondary_y": True}], [{}]])

    # 5.1 Show the Daily Stock Prices (Last 3 Months)
    fig.add_trace(go.Candlestick(x=df.index,
                                open=df['Open'],
                                high=df['High'],
                                low=df['Low'],
                                close=df['Close'],
                                name='Daily Price'),
                row=1, col=1)

    # 5.2 Show the Trends on the Same Chart (Full Year)
    fig.add_trace(go.Scatter(x=df.index, y=df['ShortTermTrend'], mode='lines', name='Short-Term Trend', line=dict(color='orange')), 
                row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['LongTermTrend'], mode='lines', name='Long-Term Trend', line=dict(color='purple')), 
                row=1, col=1)

    # 5.3 Show When to Buy or Sell (Last 3 Months)
    buy_signals = df.loc[df['Action'] == 'Buy']
    sell_signals = df.loc[df['Action'] == 'Sell']
    fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'], mode='markers', name='Buy', 
                            marker=dict(symbol='triangle-up', size=10, color='green')),
                row=1, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Close'], mode='markers', name='Sell',
                            marker=dict(symbol='triangle-down', size=10, color='red')),
                row=1, col=1, secondary_y=False)

    # 5.4 Show How Quickly the Price is Changing (Last 3 Months)
    fig.add_trace(go.Scatter(x=df.index, y=df['PriceChangeSpeed'], mode='lines', name='Price Change Speed'), 
                row=2, col=1)

    # 5.5 Show if Price Change is Too Fast or Too Slow (Last 3 Months)
    fig.add_hline(y=70, line_width=1, line_dash="dash", line_color="red", row=2, col=1)  
    fig.add_hline(y=30, line_width=1, line_dash="dash", line_color="green", row=2, col=1) 
    # 6. Simple Future Price Prediction (Extrapolation)
    last_close = df['Close'][-1]  # Get the last closing price
    last_short_term_trend = df['ShortTermTrend'][-1]  
    last_long_term_trend = df['LongTermTrend'][-1]

    # Predict 7 days into the future (adjust as needed)
    future_dates = pd.date_range(start=df.index[-1], periods=8, freq='D')[1:]  # Exclude today
    future_short_term_trend = [last_short_term_trend] * len(future_dates)  # Assume trend continues
    future_long_term_trend = [last_long_term_trend] * len(future_dates)  # Assume trend continues

    # Crude price prediction (average of trends)
    future_prices = [(short + long) / 2 for short, long in zip(future_short_term_trend, future_long_term_trend)]

    # Add prediction to chart
    fig.add_trace(go.Scatter(x=future_dates, y=future_prices, mode='lines', name='Predicted Price', line=dict(color='gray', dash='dot')), row=1, col=1)


    # 6. Finalize and Show the Chart
    fig.update_layout(
        title=f"{stock_name} - Simple Stock Analysis (Last 3 Months)",
        yaxis_title='Price (INR)',
        yaxis2_title='Price Change Speed',
        showlegend=True,
        xaxis_rangeslider_visible=False  
    )

    fig.show()