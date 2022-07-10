import bs4, requests

def get_input_url():
    """
    Get input url to scrape from user.
    """
    print("Are you ready to scrape a webpage?")
    page_link = input("Enter the url you want to scrape:\n")

    print(f"Thank you! I'm scraping {page_link}...\n")

    return page_link

def get_page_html(page_link):
    """
    Send a get HTTP request to page_link and receive the html of the page.
    raise_for_status verifies that the request is good.
    """
    print("Parsing the page html...\n")
    response = requests.get(page_link)
    response.raise_for_status()
    page_html = bs4.BeautifulSoup(response.text, "html.parser")
    print(page_html)

def main():
    """ 
    Run all the program functions.
    """
    page_link = get_input_url()
    page_html = get_page_html(page_link)

main()