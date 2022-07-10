import bs4, requests

page_link = "https://pietralikelocals.com/"

def get_page_html(page_link):
    """
    Send a get HTTP request to page_link and receive the html of the page.
    raise_for_status verifies that the request is good.
    """
    response = requests.get(page_link)
    response.raise_for_status()
    page_html = bs4.BeautifulSoup(response.text, "html.parser")
    print(page_html)

def main ():
    page_html = get_page_html(page_link)

main()