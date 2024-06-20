from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://www.amazon.com")

# Wait for the user to log in
input("Please log in to your Amazon account and press Enter to continue...")

# Verify login by checking for the presence of an element that appears after login
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "nav-orders")))

# Click on the Orders link
orders_link = driver.find_element(By.ID, "nav-orders")
orders_link.click()

# Wait for the orders page to load
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "your-orders-content-container")))

# Start IPython shell
from IPython import embed
embed()
