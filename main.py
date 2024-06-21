import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from decimal import Decimal, getcontext
from datetime import datetime, timedelta
from colorama import Fore, Style, init
import re

# Initialize colorama
init(autoreset=True)

# Set the precision high enough for currency calculations
getcontext().prec = 6

HELP_TEXT = """
Available commands:
  list            - List all scraped orders
  open <number>   - Open the order details page in the browser (e.g., open 1)
  search <text>   - Search orders by text pattern (e.g., search groceries)
  help            - Display this help text
  exit            - Exit the program
"""

def parse_order_date(date_str):
    try:
        return datetime.strptime(date_str, '%B %d, %Y')
    except ValueError:
        return None

def extract_order_amount(order_info, is_grocery=False):
    try:
        if is_grocery:
            order_amount_element = order_info.find_element(By.CLASS_NAME, "yohtmlc-order-total").find_element(By.CLASS_NAME, "a-color-secondary.value")
        else:
            order_amount_element = order_info.find_element(By.CLASS_NAME, "a-span2").find_element(By.CLASS_NAME, "a-size-base.a-color-secondary")
        amount_text = order_amount_element.text.replace('$', '').replace(',', '').strip()
        return Decimal(amount_text)
    except Exception as e:
        print(Fore.RED + f"Failed to find order amount: {e}")
        raise

def extract_order_date(order_info, is_grocery=False):
    try:
        if is_grocery:
            order_date_element = order_info.find_element(By.CLASS_NAME, "a-column.a-span3").find_element(By.CLASS_NAME, "a-color-secondary.value")
        else:
            order_date_element = order_info.find_element(By.CLASS_NAME, "a-span3").find_element(By.CLASS_NAME, "a-size-base.a-color-secondary")
        order_date_str = order_date_element.text
        return parse_order_date(order_date_str), order_date_str
    except Exception as e:
        print(Fore.RED + f"Failed to find order date: {e}")
        raise

def extract_product_titles(order, is_grocery=False):
    if is_grocery:
        return ["groceries"]
    
    product_titles = []
    order_detail_box = order.find_element(By.CLASS_NAME, "delivery-box")
    try:
        product_elements = order_detail_box.find_elements(By.CLASS_NAME, "yohtmlc-product-title") 
        for product_element in product_elements:
            product_title = product_element.text.strip()
            if product_title:
                product_titles.append(product_title)
        if not product_titles:
            raise ValueError("No product titles found")
    except Exception as e:
        print(Fore.RED + f"Failed to find product titles: {e}")
        raise
    return product_titles

def is_grocery_order(order_info):
    try:
        order_class = order_info.get_attribute("class")
        is_grocery = "order-info" in order_class
        return is_grocery
    except Exception as e:
        print(Fore.RED + f"Failed to determine if grocery order: {e}")
        raise

def extract_order_link(order):
    try:
        link_element = order.find_element(By.CLASS_NAME, "a-link-normal")
        return link_element.get_attribute("href")
    except Exception as e:
        print(Fore.RED + f"Failed to find order link: {e}")
        raise

def scrape_orders(driver, start_date, end_date):
    orders = []
    page_number = 1
    while True:
        order_cards = driver.find_elements(By.CLASS_NAME, "order-card")
        if not order_cards:
            break

        for order in order_cards:
            try:
                try:
                    order_info = order.find_element(By.CLASS_NAME, "order-header")
                except:
                    order_info = order.find_element(By.CLASS_NAME, "order-info")

                is_grocery = is_grocery_order(order_info)
                order_amount = extract_order_amount(order_info, is_grocery)
                order_date, order_date_str = extract_order_date(order_info, is_grocery)

                if order_date < start_date:
                    return orders
                
                if start_date <= order_date <= end_date:
                    product_titles = extract_product_titles(order, is_grocery)
                    order_link = extract_order_link(order)
                    if product_titles:
                        orders.append((order_date_str, order_amount, product_titles, order_link))
            except Exception as inner_e:
                print(Fore.RED + f"Failed to process an order: {inner_e}")
                print(Fore.RED + "Stopping execution for debugging purposes. Please inspect the browser.")
                return orders

        try:
            next_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Next')]")
            next_button.click()
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "your-orders-content-container")))
            page_number += 1
        except Exception as e:
            break

    return orders

def main(start_date, end_date):
    print(Fore.CYAN + "Welcome to Personal Amazon Order Scraper")
    print(Fore.CYAN + f"Scraping orders from {start_date.date()} to {end_date.date()}")
    print(Fore.WHITE + "Bringing up the Amazon home page, LOGIN manually, RETURN HERE AND PRESS ENTER to continue")

    driver = webdriver.Chrome()
    driver.get("https://www.amazon.com")

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "nav-link-accountList")))
        sign_in_link = driver.find_element(By.ID, "nav-link-accountList")
        sign_in_link.click()
    except Exception as e:
        print(Fore.RED + f"Failed to click sign-in link: {e}")
        driver.quit()
        sys.exit(1)

    input(Fore.WHITE + "Please log in to your Amazon account and press Enter to continue...")

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "nav-orders")))
        print(Fore.GREEN + "Login successful!")
    except Exception as e:
        print(Fore.RED + "Login failed. Please try again.")
        driver.quit()
        sys.exit(1)

    try:
        orders_link = driver.find_element(By.ID, "nav-orders")
        orders_link.click()
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "your-orders-content-container")))
        print(Fore.GREEN + "Orders page loaded successfully!")
        print(Fore.GREEN + "Scraping orders, you will see order pages scrolling in your browser")
    except Exception as e:
        print(Fore.RED + f"Failed to load the orders page: {e}")
        driver.quit()
        sys.exit(1)

    try:
        scraped_orders = scrape_orders(driver, start_date, end_date)
        if not scraped_orders:
            print(Fore.YELLOW + "No orders found.")
        
        print(Fore.GREEN + "Orders have been scraped. You can now query by entering an amount, 'list' to list all orders, 'open <order number>' to open an order, 'search <text>' to search orders, or 'exit' to quit.")
        print(Fore.WHITE + HELP_TEXT)

        while True:
            user_input = input(Fore.WHITE + "Enter your command: ")
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'list':
                for idx, (order_date, order_amount, product_titles, order_link) in enumerate(scraped_orders, start=1):
                    print(Fore.YELLOW + f"Order #{idx}:")
                    print(Fore.YELLOW + f"  Order Date: {Fore.CYAN}{order_date}")
                    print(Fore.YELLOW + f"  Order Amount: {Fore.CYAN}${order_amount:.2f}")
                    for product_title in product_titles:
                        print(Fore.YELLOW + f"  Product Title: {Fore.CYAN}{product_title}")
                continue
            elif user_input.lower().startswith('open '):
                try:
                    order_idx = int(user_input.split()[1]) - 1
                    if 0 <= order_idx < len(scraped_orders):
                        order_link = scraped_orders[order_idx][3]
                        driver.get(order_link)
                        print(Fore.GREEN + "Order details page opened in the browser.")
                    else:
                        print(Fore.RED + "Invalid order number. Please try again.")
                except (IndexError, ValueError):
                    print(Fore.RED + "Invalid input. Please enter a valid order number after 'open'.")
                continue
            elif user_input.lower().startswith('search '):
                search_term = user_input[7:].strip().lower()
                matching_orders = [(idx, order) for idx, order in enumerate(scraped_orders) if search_term in order[0].lower() or search_term in str(order[1]) or any(search_term in title.lower() for title in order[2])]
                
                if matching_orders:
                    print(Fore.GREEN + "Matching orders found:")
                    for idx, (order_date, order_amount, product_titles, order_link) in matching_orders:
                        print(Fore.YELLOW + f"Order #{idx+1}:")
                        print(Fore.YELLOW + f"  Order Date: {Fore.CYAN}{order_date}")
                        print(Fore.YELLOW + f"  Order Amount: {Fore.CYAN}${order_amount:.2f}")
                        for product_title in product_titles:
                            print(Fore.YELLOW + f"  Product Title: {Fore.CYAN}{product_title}")
                    open_order_input = input(Fore.WHITE + "Enter 'open <order number>' to open an order, or press Enter to return to the main menu: ")
                    if open_order_input.lower().startswith('open '):
                        try:
                            order_idx = int(open_order_input.split()[1]) - 1
                            if 0 <= order_idx < len(scraped_orders):
                                order_link = scraped_orders[order_idx][3]
                                driver.get(order_link)
                                print(Fore.GREEN + "Order details page opened in the browser.")
                            else:
                                print(Fore.RED + "Invalid order number. Please try again.")
                        except (IndexError, ValueError):
                            print(Fore.RED + "Invalid input. Please enter a valid order number after 'open'.")
                else:
                    print(Fore.YELLOW + "No matching orders found.")
            elif user_input.lower() == 'help':
                print(Fore.WHITE + HELP_TEXT)
            else:
                try:
                    target_amount_decimal = Decimal(user_input.replace('$', '').strip())
                    matching_orders = [order for order in scraped_orders if order[1] == target_amount_decimal]
                    
                    if matching_orders:
                        print(Fore.GREEN + "Matching orders found:")
                        for idx, (order_date, order_amount, product_titles, order_link) in enumerate(matching_orders, start=1):
                            print(Fore.YELLOW + f"Order #{idx}:")
                            print(Fore.YELLOW + f"  Order Date: {Fore.CYAN}{order_date}")
                            print(Fore.YELLOW + f"  Order Amount: {Fore.CYAN}${order_amount:.2f}")
                            for product_title in product_titles:
                                print(Fore.YELLOW + f"  Product Title: {Fore.CYAN}{product_title}")
                        open_order_input = input(Fore.WHITE + "Enter 'open <order number>' to open an order, or press Enter to return to the main menu: ")
                        if open_order_input.lower().startswith('open '):
                            try:
                                order_idx = int(open_order_input.split()[1]) - 1
                                if 0 <= order_idx < len(scraped_orders):
                                    order_link = scraped_orders[order_idx][3]
                                    driver.get(order_link)
                                    print(Fore.GREEN + "Order details page opened in the browser.")
                                else:
                                    print(Fore.RED + "Invalid order number. Please try again.")
                            except (IndexError, ValueError):
                                print(Fore.RED + "Invalid input. Please enter a valid order number after 'open'.")
                    else:
                        print(Fore.YELLOW + "No matching orders found.")
                except Exception as e:
                    print(Fore.RED + "Invalid input. Please enter a valid amount, 'list', 'search <text>', 'open <order number>', or 'exit'.")
    except Exception as e:
        print(Fore.RED + f"Failed to scrape orders: {e}")
        print(Fore.RED + "Stopping execution for debugging purposes.")
        return

    print(Fore.GREEN + "Session ended.")
    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        start_date_str = sys.argv[1]
        end_date_str = sys.argv[2]
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            print(Fore.RED + "Invalid date format. Please use YYYY-MM-DD.")
            sys.exit(1)
    else:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=30)
    
    print(Fore.CYAN + f"Scraping orders from {start_date.date()} to {end_date.date()}")
    main(start_date, end_date)
