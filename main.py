import sys
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from decimal import Decimal, getcontext

# Set the precision high enough for currency calculations
getcontext().prec = 6

def main(target_amount_decimal):
    driver = webdriver.Chrome()
    driver.get("https://www.amazon.com")

    # Click on the sign-in link
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "nav-link-accountList")))
    sign_in_link = driver.find_element(By.ID, "nav-link-accountList")
    sign_in_link.click()

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
        print("Failed to load the orders page. Please try again.")
        driver.quit()
        sys.exit(1)

    # Scrape orders
    try:
        orders = driver.find_elements(By.CLASS_NAME, "order-card")
        matching_orders = []

        for order in orders:
            try:
                order_info = order.find_element(By.CLASS_NAME, "a-box-inner")
                
                # Extract order amount
                order_amount_element = order_info.find_element(By.XPATH, ".//div[contains(@class, 'a-span2')]//span[@class='a-size-base a-color-secondary']")
                order_amount = Decimal(order_amount_element.text.replace('$', '').replace(',', '').strip())

                # Extract order date
                order_date_element = order_info.find_element(By.XPATH, ".//div[contains(@class, 'a-span3')]//span[@class='a-size-base a-color-secondary']")
                order_date = order_date_element.text
                
                # Extract product title
                product_title = "N/A"
                try:
                    product_title_element = order.find_element(By.CLASS_NAME, "yohtmlc-product-title")
                    product_title = product_title_element.text
                except Exception as e:
                    pass  # Fail silently if product title is not found directly in order-card

                # Try finding product title within the a-box-inner if not found in order-card
                if product_title == "N/A":
                    try:
                        product_title_element = order_info.find_element(By.CLASS_NAME, "yohtmlc-product-title")
                        product_title = product_title_element.text
                    except Exception as e:
                        pass  # Fail silently if product title is not found within a-box-inner

                if order_amount == target_amount_decimal:
                    matching_orders.append((order_date, order_amount, product_title))
            except Exception as inner_e:
                pass  # Fail silently if any other issue occurs while processing an order
        
        if matching_orders:
            print("Matching orders found:")
            for order_date, order_amount, product_title in matching_orders:
                print(f"Order Date: {order_date}, Order Amount: ${order_amount:.2f}, Product Title: {product_title}")
        else:
            print("No matching orders found.")
    except Exception as e:
        print("Failed to scrape orders.")
        driver.quit()
        sys.exit(1)

    input("Press Enter to close the browser...")
    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <target_amount>")
        sys.exit(1)
    
    raw_target_amount = sys.argv[1]

    # Correctly convert target_amount to Decimal
    target_amount_decimal = Decimal(raw_target_amount.replace('$', '').strip())

    main(target_amount_decimal)
