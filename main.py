import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from decimal import Decimal, getcontext
from datetime import datetime, timedelta

# Set the precision high enough for currency calculations
getcontext().prec = 6

def parse_order_date(date_str):
    try:
        return datetime.strptime(date_str, '%B %d, %Y')
    except ValueError:
        return None

def extract_order_amount(order_info, is_grocery=False):
    try:
        if is_grocery:
            order_amount_element = order_info.find_element(By.XPATH, ".//div[contains(@class, 'yohtmlc-order-total')]//span[@class='a-color-secondary value']")
        else:
            order_amount_element = order_info.find_element(By.XPATH, ".//div[contains(@class, 'a-span2')]//span[@class='a-size-base a-color-secondary']")
        amount_text = order_amount_element.text.replace('$', '').replace(',', '').strip()
        return Decimal(amount_text)
    except Exception as e:
        print(f"Failed to find order amount: {e}")
        raise

def extract_order_date(order_info, is_grocery=False):
    try:
        if is_grocery:
            order_date_element = order_info.find_element(By.XPATH, ".//div[contains(@class, 'a-column a-span3')]//span[@class='a-color-secondary value']")
        else:
            order_date_element = order_info.find_element(By.XPATH, ".//div[contains(@class, 'a-span3')]//span[@class='a-size-base a-color-secondary']")
        order_date_str = order_date_element.text
        return parse_order_date(order_date_str), order_date_str
    except Exception as e:
        print(f"Failed to find order date: {e}")
        raise

def extract_product_titles(order, is_grocery=False):
    if is_grocery:
        return ["groceries"]
    
    product_titles = []
    # order details are in a div with the class name "delivery box"
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
        print(f"Failed to find product titles: {e}")
        raise
    return product_titles

def is_grocery_order(order_info):
    try:
        # Check if the class is "order-info" which indicates a grocery order
        order_class = order_info.get_attribute("class")
        is_grocery = "order-info" in order_class
        return is_grocery
    except Exception as e:
        print(f"Failed to determine if grocery order: {e}")
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
                # Find the order-info or order-header
                try:
                    order_info = order.find_element(By.CLASS_NAME, "order-header")
                    print("Processing non-grocery order")
                except:
                    order_info = order.find_element(By.CLASS_NAME, "order-info")
                    print("Processing grocery order")

                is_grocery = is_grocery_order(order_info)
                order_amount = extract_order_amount(order_info, is_grocery)
                order_date, order_date_str = extract_order_date(order_info, is_grocery)

                if order_date < start_date:
                    print(f"Order date {order_date} is older than start date {start_date}. Stopping further scraping.")
                    return orders
                
                if start_date <= order_date <= end_date:
                    product_titles = extract_product_titles(order, is_grocery)
                    if product_titles:
                        orders.append((order_date_str, order_amount, product_titles))
                        print(f"Appended order: Date: {order_date_str}, Amount: {order_amount}, Titles: {product_titles}")
            except Exception as inner_e:
                print(f"Failed to process an order: {inner_e}")
                print("Stopping execution for debugging purposes. Please inspect the browser.")
                return orders

        # Check if there is a next page
        try:
            next_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Next')]")
            next_button.click()
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "your-orders-content-container")))
            page_number += 1
        except Exception as e:
            break  # No more pages

    return orders

def main(start_date, end_date):
    driver = webdriver.Chrome()
    driver.get("https://www.amazon.com")

    # Click on the sign-in link
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "nav-link-accountList")))
        sign_in_link = driver.find_element(By.ID, "nav-link-accountList")
        sign_in_link.click()
    except Exception as e:
        print(f"Failed to click sign-in link: {e}")
        driver.quit()
        sys.exit(1)

    # Wait for the user to log in
    input("Please log in to your Amazon account and press Enter to continue...")

    # Verify login by checking for the presence of an element that appears after login
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "nav-orders")))
        print("Login successful!")
    except Exception as e:
        print("Login failed. Please try again.")
        driver.quit()
        sys.exit(1)

    # Click on the Orders link
    try:
        orders_link = driver.find_element(By.ID, "nav-orders")
        orders_link.click()
        
        # Wait for the orders page to load
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "your-orders-content-container")))
        print("Orders page loaded successfully!")
    except Exception as e:
        print(f"Failed to load the orders page: {e}")
        driver.quit()
        sys.exit(1)

    # Scrape orders
    try:
        scraped_orders = scrape_orders(driver, start_date, end_date)
        if not scraped_orders:
            print("No orders found.")
        
        print("Order scraping completed.")
        
        while True:
            target_amount_input = input("Enter the target amount (or type 'exit' to quit, 'list' to list all orders): ")
            if target_amount_input.lower() == 'exit':
                break
            elif target_amount_input.lower() == 'list':
                for order_date, order_amount, product_titles in scraped_orders:
                    print(f"Order Date: {order_date}, Order Amount: ${order_amount:.2f}")
                    for product_title in product_titles:
                        print(f"  Product Title: {product_title}")
                continue
            
            try:
                target_amount_decimal = Decimal(target_amount_input.replace('$', '').strip())
            except Exception as e:
                print("Invalid amount. Please try again.")
                continue
            
            matching_orders = [order for order in scraped_orders if order[1] == target_amount_decimal]
            
            if matching_orders:
                print("Matching orders found:")
                for order_date, order_amount, product_titles in matching_orders:
                    print(f"Order Date: {order_date}, Order Amount: ${order_amount:.2f}")
                    for product_title in product_titles:
                        print(f"  Product Title: {product_title}")
            else:
                print("No matching orders found.")

    except Exception as e:
        print(f"Failed to scrape orders: {e}")
        print("Stopping execution for debugging purposes.")
        return  # Keep the browser open for debugging

    print("Session ended.")
    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        start_date_str = sys.argv[1]
        end_date_str = sys.argv[2]
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            sys.exit(1)
    else:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=30)
    
    print(f"Scraping orders from {start_date.date()} to {end_date.date()}")
    main(start_date, end_date)
