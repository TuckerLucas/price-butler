#!/usr/bin/env python3

import requests
import smtplib
import json
import sys
import os
import re
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from email.mime.text import MIMEText

# Load .env file
load_dotenv()

# -------------------------------
# LOAD PRODUCTS.JSON
# -------------------------------
json_file = "products.json"

if not os.path.exists(json_file):
    print(f"Error: {json_file} not found.")
    sys.exit(1)

with open(json_file, "r") as f:
    products_to_track = json.load(f)

# -------------------------------
# SCRAPER SETUP
# -------------------------------
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

results = []

def extract_pid_from_url(url):
    match = re.search(r'-(\d+)\.html', url)
    return match.group(1) if match else None

# -------------------------------
# MAIN SCRAPING LOOP
# -------------------------------
for product in products_to_track:
    name = product["name"]
    url = product["url"]
    pid = extract_pid_from_url(url)
    base_price = product["base_price"]

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # -------------------------------
        # FIXED PRICE EXTRACTION
        # -------------------------------
        price_span = soup.select_one('span.pwc-tile--price-primary')

        if not price_span:
            continue

        raw_price = price_span.get_text(strip=True)

        normalized_price = (
            raw_price
            .replace('€', '')
            .replace('\xa0', '')
            .replace(',', '.')
        )

        try:
            current_price = float(normalized_price)
        except ValueError:
            continue

        # -------------------------------
        # PID DOUBLE-CHECK
        # -------------------------------
        page_pid_div = soup.select_one(
            'div.row.no-gutters.product-detail.product-wrapper'
        )
        page_pid = page_pid_div.get('data-pid') if page_pid_div else None

        if pid and page_pid and page_pid != pid:
            continue

        # -------------------------------
        # PRICE COMPARISON (ONLY CHANGES)
        # -------------------------------
        if current_price < base_price:
            discount = 100 - (current_price * 100) / base_price
            results.append(
                f"""
                <li>
                    {name}: €{current_price:.2f}
                    (was €{base_price:.2f},
                    <span style="color: green; font-weight: bold;">
                        {discount:.0f}% off
                    </span>)
                </li>
                """
            )

        elif current_price > base_price:
            increase = ((current_price * 100) / base_price) - 100
            results.append(
                f"""
                <li>
                    {name}: €{current_price:.2f}
                    (was €{base_price:.2f},
                    <span style="color: red; font-weight: bold;">
                        {increase:.0f}% increase
                    </span>)
                </li>
                """
            )

        # Unchanged prices are ignored

    except Exception:
        continue

# -------------------------------
# EMAIL BODY
# -------------------------------
subject = "Daily Price Report"

if not results:
    body = "<p>No price changes detected today.</p>"
else:
    body = f"""
    <html>
        <body>
            <h3>Daily Price Report</h3>
            <ul>
                {''.join(results)}
            </ul>
        </body>
    </html>
    """

# -------------------------------
# EMAIL CONFIG
# -------------------------------
sender = os.getenv("EMAIL_SENDER")
password = os.getenv("EMAIL_PASSWORD")
recipient = os.getenv("EMAIL_RECIPIENT")

def send_email(subject, body, sender, recipients, password):
    try:
        msg = MIMEText(body, "html")
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = (
            ', '.join(recipients)
            if isinstance(recipients, list)
            else recipients
        )

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, msg.as_string())

        print("✅ Email sent successfully!")

    except Exception as e:
        print(f"❌ Failed to send daily report.\n\nError: {str(e)}")

send_email(subject, body, sender, recipient, password)