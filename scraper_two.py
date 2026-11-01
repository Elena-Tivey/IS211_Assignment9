import requests
from bs4 import BeautifulSoup

URL = "https://finance.yahoo.com/quote/AAPL/history?p=AAPL"
TITLE = "Apple (AAPL) Historical Prices"

# Yahoo blocks requests that don't look like a real browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

def get_soup(url):
    """Download the page and return a BeautifulSoup object."""
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def find_history_table(soup):
    """Return the table that has the 'Adj Close' column."""
    for table in soup.find_all("table"):
        if "Adj Close" in table.get_text():
            return table
    return None

def find_column_positions(table):
    """Work out which column holds the Date and which holds the Close price."""
    date_col = 0   # default positions, used if the headers can't be read
    close_col = 4

    header_cells = table.find("tr").find_all("th")
    for i, th in enumerate(header_cells):
        text = th.get_text(" ", strip=True)
        if text.startswith("Date"):
            date_col = i
        elif text.startswith("Close"):   # 'Adj Close' starts with 'Adj', so it is skipped
            close_col = i

    return date_col, close_col

def get_prices(table):
    """Return a list of (date, close_price) for every row of the table."""
    date_col, close_col = find_column_positions(table)
    prices = []

    for tr in table.find_all("tr"):
        cells = tr.find_all("td")

        # Normal rows have 7 cells. Dividend/split rows have fewer, so skip them.
        if len(cells) < 7:
            continue

        date = cells[date_col].get_text(strip=True)
        close = cells[close_col].get_text(strip=True)
        prices.append((date, close))

    return prices

def print_prices(prices):
    """Print the dates and close prices in neat columns."""
    print(TITLE)
    print("=" * len(TITLE))
    print()

    print(f"{'Date':<15} | {'Close Price':>12}")
    print("-" * 15 + "-+-" + "-" * 12)

    for date, close in prices:
        print(f"{date:<15} | {close:>12}")

    print(f"\nTotal days shown: {len(prices)}")

def main():
    print("Running apple stock scraper...\n")

    try:
        soup = get_soup(URL)
    except requests.exceptions.RequestException as error:
        print("Could not load the page:", error)
        print("If you see 429 or 403, Yahoo is blocking the request. Wait a minute and try again.")
        return

    table = find_history_table(soup)
    if table is None:
        print("Could not find the price table on the page.")
        return

    prices = get_prices(table)
    print_prices(prices)

if __name__ == "__main__":
    main()