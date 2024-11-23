"""This script serves as a skeleton template for synchronous AgentQL scripts."""

import logging

import agentql
from agentql.ext.playwright.sync_api import Page
from playwright.sync_api import sync_playwright

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Set the URL to the desired website
URL = "https://fund.cnyes.com/detail/%E9%A6%96%E6%BA%90%E6%8A%95%E8%B3%87%E7%92%B0%E7%90%83%E5%82%98%E5%9E%8B%E5%9F%BA%E9%87%91-%E9%A6%96%E5%9F%9F%E7%9B%88%E4%BF%A1%E6%97%A5%E6%9C%AC%E8%82%A1%E7%A5%A8%E5%9F%BA%E9%87%91%E7%AC%AC/B610022/"


def main():
    with sync_playwright() as p, p.chromium.launch(headless=False) as browser:
        # Create a new page in the browser and wrap it to get access to the AgentQL's querying API
        page = agentql.wrap(browser.new_page())

        # Navigate to the desired URL
        page.goto(URL)

        get_response(page)


def get_response(page: Page):
    query = """
{
    historical_price[] {
          date
          price
        }
}
    """

    response = page.query_data(query)

    # For more details on how to consume the response, refer to the documentation at https://docs.agentql.com/intro/main-concepts
    print(response)


if __name__ == "__main__":
    main()
