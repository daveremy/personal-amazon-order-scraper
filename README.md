
# Personal Amazon Order Scraper

This simple project was created because of a problem I was having when trying to reconcile my budget and put Amazon items into a budget category. From my bank transactions I knew I did an Amazon order and the amount but nothing else. I first looked for an API from Amazon to look the transaction up but no luck. So this is a Python-based web scraping tool that navigates to the Amazon page, waits for you to log into your Amazon account (possibly answer a CAPTCHA challenges), navigates to the orders page, and scrapes order details into memory within a specified date range. You can then enter an amount and get back the product information on the order.

The script uses Selenium for web automation.

## Disclaimer

This project is for personal use and educational purposes only. Use it at your own risk. The author is not responsible for any misuse or damage that may occur.

## Features

- Logs into an Amazon account.
- Navigates to the orders page.
- Scrapes order details including order date, amount, and product titles.
- Outputs all orders within a specified date range.
- Allows searching for orders by a specific amount.

## Limitations
- If there are multiple products in an order it provides the description of each but doesn't tell you how much for each
- Grocery orders just come back with "Grocery" for the description

## Requirements

- Python 3.6+
- Google Chrome
- ChromeDriver (can be installed with your package manager)

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/personal-amazon-order-scraper.git
    cd personal-amazon-order-scraper
    ```

2. **Create a virtual environment:**

    ```sh
    python -m venv venv
    ```

3. **Activate the virtual environment:**

    - On Windows:

        ```sh
        venv\Scripts\activate
        ```

    - On macOS/Linux:

        ```sh
        source venv/bin/activate
        ```

4. **Install the required packages:**

    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. **Run the script:**

    - Default is scrape orders for the last 30 days
        ```sh
        python main.py
        ```
    - If you want you can specify a date range
        ```sh
        python main.py YYYY-MM-DD YYYY-MM-DD
        ```

        Replace `YYYY-MM-DD` with the start and end dates for the order scraping period. For example:
        ```sh
        python main.py 2024-05-01 2024-06-01
        ```

2. **Follow the prompts:**

    - Log in to your Amazon account when the browser opens.
    - Press Enter in the terminal once you have logged in.

3. **View the results:**

    - To search for orders by a specific amount, enter the amount when prompted.
    - To list all scraped orders, type `list` when prompted.
    - To exit the script, type `exit` when prompted.

## .gitignore

A `.gitignore` file is included to prevent unnecessary files from being committed to the repository. It ignores Python bytecode, virtual environments, logs, and other temporary files.

## requirements.txt

A `requirements.txt` file is included to list the dependencies required for the project. To install these dependencies, run:

```sh
pip install -r requirements.txt
```
