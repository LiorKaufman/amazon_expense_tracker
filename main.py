import os
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import requests
import numpy as np


def to_float(x):
    try:
        return float(x)
    except ValueError:
        return np.nan


class AmazonScraper:
    def __init__(self, email, password, year, options):
        self.email = email
        self.password = password
        self.year = year
        self.driver = webdriver.Chrome(options=options)

    def save_screenshot(self, filename):
        self.driver.save_screenshot(filename)

    def wait_for(self, seconds):
        WebDriverWait(self.driver, seconds)

    def login(self):
        print("Starting login process")
        self.navigate_to_login_page()
        self.wait_for(2)
        print("Entering email")
        self.enter_email()
        self.save_screenshot("email_entered.png")
        self.click_continue()
        self.wait_for(3)
        print("Entering password")
        self.enter_password()
        self.save_screenshot("password_entered.png")
        print("Sign in")
        self.click_sign_in()
        input("wait for human to complete captcha")
        self.wait_for(10)
        self.save_screenshot("logged_in.png")
        self.wait_for(10)
        self.save_screenshot("loged_2.png")

    def get_orders(self):
        print("Starting to get orders")
        self.click_orders()
        self.wait_for(8)
        self.save_screenshot("order_page.png")
        print("Selecting year")
        self.click_year_select_filter()
        self.wait_for(5)
        self.save_screenshot("select_pressed.png")
        page = 0
        while True:
            page += 1
            print(f"scraping orders page {page}")
            self.save_ordered_products()
            self.wait_for(2)
            try:
                next_button = self.driver.find_element(
                    By.CSS_SELECTOR, '.a-last a')
                next_button.click()
            except NoSuchElementException:
                break

    def get_title(self, soup):
        try:
            # Outer Tag Object
            title = soup.find("span", attrs={"id": "productTitle"})

            # Inner NavigatableString Object
            title_value = title.text

            # Title as a string value
            title_string = title_value.strip()

        except AttributeError:
            title_string = ""

        return title_string

    def get_price(self, soup):
        try:
            price = soup.find(
                "span", attrs={"id": "priceblock_ourprice"}
            ).string.strip()
        except AttributeError:
            try:
                # If there is some deal price
                price = soup.find(
                    "span", attrs={"class": "a-offscreen"}).string.strip()
            except:
                price = ""

        return price

    def get_categories(self, soup, title):
        try:
            categories_div = soup.find(
                "div", attrs={"id": "wayfinding-breadcrumbs_container"}
            )
            categories = categories_div.find_all(
                "a", attrs={"class": "a-link-normal a-color-tertiary"}
            )
            category_list = [category.get_text(strip=True)
                             for category in categories]
        except AttributeError:
            print(f"Coudn't find categories for {title}")
            category_list = []
        return category_list

    def get_products_as_df(self) -> pd.DataFrame:
        with open("filtered_elements.html", "r") as f:
            html_content = f.read()

        HEADERS = {"User-Agent": "", "Accept-Language": "en-US, en;q=0.5"}

        soup = BeautifulSoup(html_content, "html.parser")
        product_links = soup.select("a.a-link-normal")
        amazon_base_url = "https://www.amazon.com"
        products = {"title": [], "price": [], "categories": []}
        for link in product_links:
            link_url = link["href"]
            product_title = link.string
            print(product_title)

            # Prepend Amazon base URL if not present
            if not link_url.startswith(amazon_base_url):
                link_url = amazon_base_url + link_url

            try:
                new_webpage = requests.get(link_url, headers=HEADERS)
                new_soup = BeautifulSoup(new_webpage.content, "html.parser")
                try:
                    products["title"].append(self.get_title(new_soup))
                    products["price"].append(self.get_price(new_soup))
                    products["categories"].append(
                        self.get_categories(new_soup, product_title))

                except NoSuchElementException:
                    print("Product not found. Skipping this product.")
                    continue
            except:
                print(f"Something went wrong when scraping - skipping this product")
                continue

        amazon_df = pd.DataFrame.from_dict(products)
        amazon_df["title"].replace("", np.nan, inplace=True)
        amazon_df = amazon_df.dropna(subset=["title"])
        amazon_df["price"] = amazon_df["price"].str.replace("$", "")
        amazon_df["price"] = amazon_df["price"].apply(to_float)
        amazon_df.dropna(subset=['price'], inplace=True)
        return amazon_df

    def navigate_to_login_page(self):
        self.driver.get(
            "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"
        )

    def enter_email(self):
        email_input = self.driver.find_element(By.NAME, "email")
        email_input.send_keys(self.email)

    def click_continue(self):
        self.driver.find_element(By.ID, "continue").click()

    def enter_password(self):
        password_input = self.driver.find_element(By.NAME, "password")
        password_input.send_keys(self.password)

    def click_sign_in(self):
        self.wait_for(3)
        self.driver.find_element(By.ID, "signInSubmit").click()
        self.wait_for(3)

    def click_orders(self):
        self.driver.find_element(By.ID, "nav-orders").click()

    def click_year_select_filter(self):
        select_element = self.driver.find_element(By.ID, "time-filter")
        select = Select(select_element)
        select.select_by_visible_text(self.year)

    def save_ordered_products(self):
        print("Downloading Orders to file")
        elements = self.driver.find_elements(
            By.CSS_SELECTOR, "div.a-fixed-left-grid-col div.a-row a.a-link-normal"
        )
        html_contents = [element.get_attribute(
            "outerHTML") for element in elements]
        with open("filtered_elements.html", "a") as f:
            for html in html_contents:
                f.write(html + "\n")

    def close(self):
        self.driver.quit()


# Replace with your Amazon email and password in the ENV file
load_dotenv()
# Clean up file
with open("filtered_elements.html", "w") as f:
    pass

email = os.getenv("AZ_USER")
password = os.getenv("AZ_PASSWORD")
option = Options()
option.page_load_strategy = 'normal'
amazon = AmazonScraper(email, password, "2022", option)
amazon.login()
amazon.get_orders()
df = amazon.get_products_as_df()
df.to_csv("amazon_data.csv", header=True, index=False)
