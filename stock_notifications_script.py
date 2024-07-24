from dotenv import load_dotenv
import os
import smtplib
import ssl
import yfinance as yf
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

load_dotenv()

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load the credentials
creds = ServiceAccountCredentials.from_json_keyfile_name('/root/Stock_Email_Notifications/service_account.json', scope)

# Authorize the client
client = gspread.authorize(creds)

# Open the Google Sheet by its name
sheet = client.open("Stock Trade Alert Signup Sheet (Responses)")

# Select the first sheet
worksheet = sheet.get_worksheet(0)

# Get all values from the first column after the first row
emails = worksheet.col_values(2)[1:]

stocks = ['AAPL', 'TSLA', 'PLTR', 'META', 'GOOG', 'SPY', 'QQQ', 'TQQQ', 'KO', 'SBUX', 'GLD', 'JNJ', 'AMGN', 'MRNA', 'NOW', 'AAL', 'SOFI', 'AMZN']

def verify_emails(email):
    regex = r"[a-zA-Z0-9\+\.-]+@+[a-zA-Z0-9_\.\+-]+[a-zA-Z0-9\+\.-]"
    return re.search(regex, email)
# Gets the stock data
def get_stock_data(ticker):
    stock_ticker = yf.Ticker(ticker)
    hist = stock_ticker.history(period="1y")

    price = hist['Close'].iloc[-1]
    week_52_high = hist['Close'].max()
    week_52_low = hist['Close'].min()

    return price, week_52_high, week_52_low

# Checks if the price is within 10% of the 52 week high or low
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
               f"Reccomended Sells/Shorts: {high_stocks}\n"
               f"Reccomended Buys: {low_stocks}\n\n\n")

    for email in emails:
        if verify_emails(email):
            send_email(message, email)
        else:
            continue


