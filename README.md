# Amazon Order History Scraper

This project allows you to extract and analyze your own Amazon order history. It uses Python, Selenium and BeautifulSoup for web scraping and DuckDB for data loading and analysis. The scraper is designed to navigate through your Amazon orders, save the details of each item and compile it into a CSV file. 

## Getting Started

Start by installing the required Python packages like Selenium, BeautifulSoup, and DuckDB. Set up your Amazon username and password in an `.env` file for secure access. 

## How it Works

The `AmazonScraper` class automates the login process and navigates through your order history pages to save the details of each order. The scraped order data is then parsed using BeautifulSoup and organized into a pandas DataFrame. This DataFrame is saved as a CSV file, allowing you to perform any desired data analysis.

You can then load this CSV into a DuckDB database, which is designed for fast analytic queries. This project provides several example SQL queries to analyze your spending by categories, specific categories, and more. 

The goal of this project is to empower you with an understanding of your personal spending habits on Amazon. Be aware that the actual navigation might vary based on the actual layout of Amazon's site and your account settings, which might require adjustments in the code.

## Note

This project is intended for personal use and not for misuse or violation of Amazon's Terms of Service. Please ensure you comply with these terms when using this tool.