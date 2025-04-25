#!/usr/bin/env python3

import requests
import smtplib
import json
import sys
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from email.mime.text import MIMEText

# Check for correct usage
if len(sys.argv) < 2:
    print("Usage: python3 scraper.py products.json")
    sys.exit(1)

json_file = sys.argv[1]

# Load products from JSON
with open(json_file, 'r') as f:
    products_to_track = json.load(f)

headers = {'User-Agent': 'Mozilla/5.0'}
results = []

for product in products_to_track:
    name = product["name"]
    pid = product["pid"]
    url = product["url"]
    base_price = product["base_price"]

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract current price
        price_wrapper = soup.find('div', class_='prices-wrapper')
        price_tag = price_wrapper.find('span', class_='value') if price_wrapper else None

        if not price_tag or not price_tag.has_attr('content'):
            results.append(f"{name}: Price not found!")
            continue

        current_price = float(price_tag['content'])

        # (Optional) Double-check PID
        page_pid_div = soup.select_one('div.row.no-gutters.product-detail.product-wrapper')
        page_pid = page_pid_div.get('data-pid') if page_pid_div else None

        if page_pid != pid:
            results.append(f"• {name}: WARNING - PID mismatch! Expected {pid}, got {page_pid or 'None'}")
            continue

        # Compare price
        if current_price < base_price:
            discount = 100 - (current_price * 100) / base_price
            results.append(f"• {name}: €{current_price:.2f} (was €{base_price:.2f}, {discount:.0f}% off)")
        elif current_price > base_price:
            increase = ((current_price * 100) / base_price) - 100
            results.append(f"• {name}: €{current_price:.2f} (was €{base_price:.2f}, {increase:.0f}% increase)")

    except Exception as e:
        results.append(f"Error fetching {name}: {str(e)}")
        continue

# Compose email
subject = "Daily Price Report"
body = "\n".join(results)

# Load credentials from .env
load_dotenv()
sender = os.getenv("EMAIL_SENDER")
password = os.getenv("EMAIL_PASSWORD")
recipient = os.getenv("EMAIL_RECIPIENT")

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients if isinstance(recipients, list) else [recipients])
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")

send_email(subject, body, sender, recipient, password)
