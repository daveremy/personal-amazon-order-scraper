# Amazon Order Scraper

This project is a Python-based web scraping tool that logs into an Amazon account, navigates to the orders page, and finds orders that match a specified amount. The script uses Selenium for web automation.

## Features

- Logs into an Amazon account.
- Navigates to the orders page.
- Scrapes order details and finds orders that match a specified amount.
- Outputs matching order details including date, amount, and product title.

## Requirements

- Python 3.6+
- Google Chrome
- ChromeDriver

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/amazon-order-scraper.git
    cd amazon-order-scraper
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

    ```sh
    python main.py '$37.50'
    ```

    Replace `'$37.50'` with the target amount you are searching for.

2. **Follow the prompts:**

    - Log in to your Amazon account when the browser opens.
    - Press Enter in the terminal once you have logged in.

3. **View the results:**

    - The script will output matching orders with details including the order date, amount, and product title.

## .gitignore

A `.gitignore` file is included to prevent unnecessary files from being committed to the repository. It ignores Python bytecode, virtual environments, logs, and other temporary files.

## Requirements.txt

A `requirements.txt` file is included to list the dependencies required for the project. To install these dependencies, run:

```sh
pip install -r requirements.txt
