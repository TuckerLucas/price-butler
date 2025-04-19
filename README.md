# Supermarket web scraper

A supermarket web scraper application that tracks product prices on [Continente](https://www.continente.pt/) coded in Python.

## Features

* Track the price of any product across any category listed on the [Continente](https://www.continente.pt/) website;
* Easily select which products to track via a configurable JSON file;
* Detect discounts and price increases on products relative to their base price;
* Email notification capabilities with price fluctuation information;
* Ability to run daily for the latest price changes.

## Setup

* **Setup the email notification infrastructure**
  + Define an email address responsible for sending the email notifications (you can create a new one, or use your own)
  + Within the sender email account you defined execute the following steps:
    * Click on your profile and select "Manage your Google Account"
    * On the left bar, select "Security"
    * Turn on 2 step verification
    * Once 2 step verification for your account is on, search for "App Passwords"
    * Create a new app password with a descriptive name (e.g. Continente web scraper), copy it and save it
  + Define an email address responsible for receiving the sent email notifications (this can be the same as the sender email address, you will just be sending emails to yourself)

* **Clone the repository**
  + ```git clone https://github.com/TuckerLucas/Price-butler```
  + ```cd Price-butler```
 
* **Install dependencies**
  + ```pip install -r requirements.txt```

* **Edit the .env file**
  + ```EMAIL_SENDER``` -> Insert the defined sender email address from above;
  + ```EMAIL_PASSWORD``` -> Insert the copied app password created on the sender email account;
  + ```EMAIL_RECIPIENT``` -> Insert the defined recipient email address;
 
* **Edit the products.json file**
  Edit this file to contain the products you wish to track. This file contains a few examples with the required parameters:
  * ```name``` -> Enter a descriptive name for your product
  * ```url``` -> Enter the URL link where the product is listed (make sure to go by category for the app to work)
  * ```pid``` -> Enter the corresponding "data-pid" number present in the HTML code of the above [Continente](https://www.continente.pt/) URL
  * ```base_price``` -> Enter the base price ("normal" price) of the product against which discounts/increases will be compared against

## Running the application

  ### Running manually
  + ```python3 ContinenteWebScraper.py products.json```

  ### Running automatically (daily)
  + ```crontab -e```
  + Insert the following line to the file: ```0 8 * * * /usr/bin/python3 /path/to/ContinenteWebScraper.py /path/to/products.json``` (this will configure your system to run the scraper everyday at 8 AM)
  + Use ```which python3``` to find the right python path on your system in case the above is not correct

## Future improvements

I plan to integrate other supermarkets into the application in the future. This will not only allow for users to know when the prices of their favourite products are at a discount, but will also allow them to compare these prices between different vendors.
