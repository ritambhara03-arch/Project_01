from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os

# Setup Selenium WebDriver
def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")
    driver_path = "./chromedriver"  # Adjust path to ChromeDriver
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Login to Amazon
def login_to_amazon(driver, email, password):
    driver.get("https://www.amazon.in/")
    driver.find_element(By.ID, "nav-link-accountList").click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_email"))).send_keys(email, Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_password"))).send_keys(password, Keys.RETURN)

# Extract product details
def scrape_category(driver, category_url):
    driver.get(category_url)
    products = []
    for page in range(1, 4):  # Adjust as needed for more pages
        time.sleep(2)
        product_elements = driver.find_elements(By.CSS_SELECTOR, "div.zg-item-immersion")
        for product in product_elements:
            try:
                product_name = product.find_element(By.CSS_SELECTOR, ".p13n-sc-truncate").text
                price = product.find_element(By.CSS_SELECTOR, ".p13n-sc-price").text
                discount = "50%"  # Placeholder, needs further parsing logic if available
                rating = product.find_element(By.CSS_SELECTOR, ".a-icon-alt").text
                seller_info = "Amazon"  # Placeholder
                images = [img.get_attribute("src") for img in product.find_elements(By.CSS_SELECTOR, ".a-section img")]

                products.append({
                    "Product Name": product_name,
                    "Price": price,
                    "Discount": discount,
                    "Rating": rating,
                    "Seller Info": seller_info,
                    "Images": images
                })
            except Exception as e:
                print(f"Error scraping product: {e}")

        # Navigate to the next page
        try:
            next_page = driver.find_element(By.CLASS_NAME, "a-last")
            next_page.click()
        except Exception:
            break  # No more pages

    return products

# Main scraper function
def amazon_scraper(email, password, categories):
    driver = setup_driver()
    try:
        login_to_amazon(driver, email, password)
        all_products = []
        for category in categories:
            products = scrape_category(driver, category)
            all_products.extend(products)
        
        # Save data to a file
        df = pd.DataFrame(all_products)
        df.to_csv("amazon_best_sellers.csv", index=False)
        print("Data saved to amazon_best_sellers.csv")
    finally:
        driver.quit()

if __name__ == "__main__":
    # User credentials (replace with your credentials)
    AMAZON_EMAIL = "your-email@example.com"
    AMAZON_PASSWORD = "your-password"

    # Amazon Best Seller category URLs
    CATEGORY_URLS = [
        "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0",
        "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",
        "https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0",
        "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0",
        # Add more categories as needed
    ]

    amazon_scraper(AMAZON_EMAIL, AMAZON_PASSWORD, CATEGORY_URLS)
