#!/usr/bin/env python3

import requests
import smtplib
import json
import sys
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from email.mime.text import MIMEText

# Get the JSON file path from command-line arguments
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
        product_tiles = soup.find_all('div', class_='col-12 col-sm-3 col-lg-2 productTile')

        pid_found = False

        for index, tile in enumerate(product_tiles):
            product_div = tile.find('div', class_='product')

            if product_div and product_div.get('data-pid') == pid:
                pid_found = True
                price_tag = tile.find('span', class_='value')

                if price_tag:
                    current_price = float(price_tag['content'])
                    if current_price < base_price:
                        discount = float(100 - (current_price*100)/base_price)
                        results.append(f"{name}: €{current_price:.2f} (was €{base_price:.2f}, {discount:.0f}% off)")
                    elif current_price > base_price:
                        increase = float(((current_price*100)/base_price) - 100)
                        results.append(f"{name}: €{current_price:.2f} (was €{base_price:.2f}, {increase:.0f}% increase)")
                    else:
                        break
        if not pid_found:
            results.append(f"{name}: NOT FOUND!")
    except Exception as e:
        results.append(f"Error fetching {name} (PID {pid}): {str(e)}")
        continue

# Compose email
subject = "Daily Price Report"
body = "\n".join(results)

load_dotenv()  # Loads from .env by default

sender = os.getenv("EMAIL_SENDER")
password = os.getenv("EMAIL_PASSWORD")
recipient = os.getenv("EMAIL_RECIPIENT")

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")

send_email(subject, body, sender, recipient, password)
