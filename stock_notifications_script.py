from dotenv import load_dotenv
import os
import smtplib
import ssl
import yfinance as yf

load_dotenv()

emails = ['amtiavkrishna2011@gmail.com', 'papadogspapa@gmail.com', 'arjunkrishna1306@gmail.com', 'krishna.ranjit1984@gmail.com', 'aarizthegamerx2@gmail.com']
stocks = ['AAPL', 'TSLA', 'PLTR', 'META', 'GOOG', 'SPY', 'QQQ', 'TQQQ', 'KO', 'SBUX', 'GLD',  'JNJ', 'AMGN', 'MRNA', 'NOW', 'AAL', 'SOFI', 'AMZN']

# Gets the stock data
def get_stock_data(ticker):
    stock_ticker = yf.Ticker(ticker)
    hist = stock_ticker.history(period="1y")

    price = hist['Close'].iloc[-1]
    week_52_high = hist['Close'].max()
    week_52_low = hist['Close'].min()

    return price, week_52_high, week_52_low

# Checks if the price is within 10% of the 52 week high or low['Close'['Close'
def check_low_high(stocks):
    high_stocks = ""
    low_stocks = ""
    
    for ticker in stocks:
        current_price, high_52week, low_52week = get_stock_data(ticker)

        # Checks if the 52 Week High is within 10% of current price
        if high_52week <= current_price * 1.1:
            high_stocks += (ticker + ', ')

        # Checks if the 52 Week Low is within 10% of current price
        elif low_52week >= current_price * 0.9:
            low_stocks += (ticker + ', ')
    
    return high_stocks.strip(', '), low_stocks.strip(', ')

# Function to send the message
def send_email(message, email):
    password = os.getenv('EMAIL_PASSWORD')
    if not password:
       print("Error: Email password not set in .env file")
       return
    sender_email = "python.testing.amitav@gmail.com"  

    context = ssl.create_default_context()
    port = 465

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, email, message)
        print("Email sent successfully")

# Main function
if __name__ == "__main__":
    high_stocks, low_stocks = check_low_high(stocks)
    message = (f"Subject: Daily Stock Alert\n\n"
               f"High Stocks: {high_stocks}\n"
               f"Low Stocks: {low_stocks}\n")

    for email in emails:
        send_email(message, email)

