import csv
import requests
from bs4 import BeautifulSoup

URL = "https://en.wikipedia.org/wiki/List_of_World_Series_champions"
OUTPUT_FILE = "world_series_champions.csv"
TITLE = "List of World Series Champions"

def get_table(url):
    """Download the page and return the table that contains 'Winning team'."""
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
    soup = BeautifulSoup(html, "html.parser")

    for t in soup.find_all("table", class_="wikitable"):
        if "Winning team" in t.get_text():
            return t
    return None

def fill_merged(row, col, pending):
    """Insert cells carried down from merged (rowspan) cells above."""
    while col in pending:
        text, remaining = pending[col]
        row.append(text)
        if remaining == 1:
            del pending[col]
        else:
            pending[col][1] -= 1
        col += 1
    return col

def parse_table(table):
    """Turn the HTML table into a list of rows, handling merged cells."""
    # Remove footnote markers like [1]
    for sup in table.find_all("sup"):
        sup.decompose()

    rows = []
    pending = {}  # column number -> [text, rows still to fill]

    for tr in table.find_all("tr"):
        row = []
        col = 0

        for cell in tr.find_all(["th", "td"]):
            col = fill_merged(row, col, pending)

            text = cell.get_text(strip=True)
            rowspan = int(cell.get("rowspan", 1))
            colspan = int(cell.get("colspan", 1))

            for _ in range(colspan):
                row.append(text)
                if rowspan > 1:
                    pending[col] = [text, rowspan - 1]
                col += 1

        fill_merged(row, col, pending)

        if row:
            rows.append(row)

    return rows

def save_csv(rows, filename):
    """Save the rows to a CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

def print_rows(rows):
    """Print the rows with aligned columns and a line under the column titles."""
    num_cols = len(rows[0])
    widths = [0] * num_cols

    for row in rows:
        if len(row) == num_cols:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], min(len(cell), 35))

    header_done = False

    for row in rows:
        if len(set(row)) == 1:
            # A title row that spans the whole table
            print("\n" + row[0])
        elif len(row) == num_cols:
            print(" | ".join(cell[:widths[i]].ljust(widths[i]) for i, cell in enumerate(row)))

            # After the first full row (the column titles), print the dashes
            if not header_done:
                print("-+-".join("-" * w for w in widths))
                header_done = True
        else:
            print(" | ".join(row))

def main():
    print("Running List of World Series Champions scraper...")

    table = get_table(URL)
    if table is None:
        print("Could not find the table.")
        return

    rows = parse_table(table)
    save_csv(rows, OUTPUT_FILE)

    print(f"Saved {len(rows)} rows to {OUTPUT_FILE}\n")

    # Title above the table
    print(TITLE)
    print("=" * len(TITLE))
    print()

    print_rows(rows)

if __name__ == "__main__":
    main()