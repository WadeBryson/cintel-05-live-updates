import asyncio
import os
from pathlib import Path
from datetime import datetime
from random import randint

# Import external packages
import pandas as pd
import yfinance as yf
from collections import deque
from dotenv import load_dotenv

# Local imports
from fetch import fetch_from_url
from util_logger import setup_logger

# Set up logger
logger, log_filename = setup_logger(__file__)


def lookup_ticker(company):
    stocks_dictionary = {
        "Tesla Inc": "TSLA",
        "General Motors Company": "GM",
        "Toyota Motor Corporation": "TM",
        "Ford Motor Company": "F",
        "Honda Motor Co": "HMC",
    }
    ticker = stocks_dictionary[company]
    return ticker



def get_stock_price(ticker):
    logger.info("Calling get_stock_price for {ticker}")
    stock_url = f"https://query1.finance.yahoo.com/v7/finance/options/{ticker}"
    logger.info(f"Calling fetch_from_url for {stock_url}")
    # result = await fetch_from_url(stock_url,"json")
    # price = result.data["optionChain"]["result"][0]["quote"]["regularMarketPrice"]
    price = randint(132, 148)
    return price


# Create or overwrite CSV with column headings
def init_csv_file(file_path):
    df_empty = pd.DataFrame(columns=["Company", "Ticker", "Time", "Stock_Price"])
    df_empty.to_csv(file_path, index=False)


# Writes new stock info to CSV
async def update_csv_stock():
    logger.info("Calling update_csv_stock")
    try:
        companies = [
            "Tesla Inc",
            "General Motors Company",
            "Toyota Motor Corporation",
            "Ford Motor Company",
            "Honda Motor Co",
        ]
        update_interval = 60  # Update every 1 minute (60 seconds)
        total_runtime = 15 * 60  # Total runtime maximum of 15 minutes
        num_updates = 50  # Keep the most recent 10 readings
        logger.info(f"update_interval: {update_interval}")
        logger.info(f"total_runtime: {total_runtime}")
        logger.info(f"num_updates: {num_updates}")

        # Use a deque to store just the last, most recent 10 readings in order
        records_deque = deque(maxlen=num_updates)

        fp = Path(__file__).parent.joinpath("data").joinpath("mtcars_stock.csv")

        # Check if the file exists, if not, create it with only the column headings
        if not os.path.exists(fp):
            init_csv_file(fp)

        logger.info(f"Initialized csv file at {fp}")

        for _ in range(num_updates):  # To get num_updates readings
            for company in companies:
                ticker = lookup_ticker(company)
                new_price = get_stock_price(ticker) # await
                time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current time
                new_record = {
                    "Company": company,
                    "Ticker": ticker,
                    "Time": time_now,
                    "Price": new_price,
                }
                records_deque.append(new_record)

            # Use the deque to make a DataFrame
            df = pd.DataFrame(records_deque)

            # Save the DataFrame to the CSV file, deleting its contents before writing
            df.to_csv(fp, index=False, mode="w")
            logger.info(f"Saving prices to {fp}")

            # Wait for update_interval seconds before the next reading
            await asyncio.sleep(update_interval)  #await

    except Exception as e:
        logger.error(f"ERROR in update_csv_stock: {e}")
