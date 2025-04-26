import smtplib
import requests
import openai
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# ========== CONFIGURATION ==========
EMAIL_ADDRESS = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_app_password'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465

OPENAI_API_KEY = 'your_openai_api_key'

# Example portfolio (customer-specific later)
PORTFOLIO = ['AAPL', 'MSFT', 'TSLA']

# ========== FETCH STOCK DATA ==========
def get_stock_data(symbols):
    stocks = []
    for symbol in symbols:
        # Replace this with a real API call (e.g., Yahoo Finance API, Finnhub)
        response = requests.get(f'https://finnhub.io/api/v1/quote?symbol={symbol}&token=###YOUR_FINNHUB_API_KEY###')
        if response.status_code == 200:
            data = response.json()
            price = data['c']
            change = ((data['c'] - data['pc']) / data['pc']) * 100 if data['pc'] != 0 else 0
            stocks.append({'symbol': symbol, 'price': round(price, 2), 'change': round(change, 2)})
        else:
            stocks.append({'symbol': symbol, 'price': 'N/A', 'change': 'N/A'})
    return stocks

# ========== GENERATE MARKET SUMMARY ==========
def generate_market_summary(stocks):
    openai.api_key = OPENAI_API_KEY
    stock_info = ", ".join([f"{stock['symbol']} {stock['change']}%" for stock in stocks])

    prompt = f"Write a short and professional stock market summary for today based on the following stock movements: {stock_info}."
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a financial newsletter writer."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# ========== BUILD EMAIL CONTENT ==========
def build_email_content(stocks, summary, customer_name):
    today = datetime.now().strftime("%B %d, %Y")

    table_rows = ""
    for stock in stocks:
        change_color = "green" if isinstance(stock['change'], (float, int)) and stock['change'] >= 0 else "red"
        table_rows += f"""
        <tr>
            <td style="border: 1px solid #ddd; padding: 8px;">{stock['symbol']}</td>
            <td style="border: 1px solid #ddd; padding: 8px;">${stock['price']}</td>
            <td style="border: 1px solid #ddd; padding: 8px; color:{change_color};">{stock['change']}%</td>
        </tr>
        """

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>📈 Daily Stock Market Report - {today}</h2>
        <p>Hello {customer_name},</p>
        <p>Here is your personalized stock update for today:</p>

        <table style="border-collapse: collapse; width: 100%;">
            <tr>
                <th style="border: 1px solid #ddd; padding: 8px;">Stock</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Price</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Change</th>
            </tr>
            {table_rows}
        </table>

        <h3>📝 Market Summary:</h3>
        <p>{summary}</p>

        <br>
        <p style="font-size:small; color:gray;">You are receiving this email because you subscribed to Daily Stock Updates.</p>
    </body>
    </html>
    """
    return html

# ========== SEND EMAIL ==========
def send_email(to_email, subject, html_content):
    msg = MIMEMultipart('alternative')
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject

    part = MIMEText(html_content, 'html')
    msg.attach(part)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        print("Connecting to SMTP server...")
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, [to_email], msg.as_string())
        print(f"Email sent to {to_email}!")

# ========== MAIN FUNCTION ==========
def main():
    customer_name = "John Doe"  # You can personalize
    customer_email = "customer_email@gmail.com"

    stocks = get_stock_data(PORTFOLIO)
    summary = generate_market_summary(stocks)
    email_content = build_email_content(stocks, summary, customer_name)
    send_email(customer_email, "📈 Your Daily Stock Market Update", email_content)

if __name__ == "__main__":
    main()
    print("Daily stock report generated and sent successfully.")
# This script fetches stock data, generates a market summary using OpenAI's GPT-3.5, and sends an email with the report.
    