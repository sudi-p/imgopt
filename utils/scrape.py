import requests
from bs4 import BeautifulSoup


def scrape_product(url):

    # Headers to make the request look like it's coming from a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Send a GET request to the URL
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Try finding the unordered list with the specific class
        ul = soup.find("ul", class_="a-unordered-list a-vertical a-spacing-mini")
        
        # Check if the unordered list was found
        if ul:
            # Extract the text from each list item
            list_items = [li.get_text(strip=True) for li in ul.find_all("li", class_="a-spacing-mini")]
        else:
            # If the above approach didn't work, try a more specific CSS selector
            list_items = [li.get_text(strip=True) for li in soup.select("ul.a-unordered-list.a-vertical.a-spacing-mini li.a-spacing-mini")]
        
        # Print the list of features
        return list_items
    else:
        return({ "message" : f"Failed to retrieve the page. Status code:{response.status_code}"})
