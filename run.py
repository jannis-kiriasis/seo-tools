import bs4, requests

page_link = "https://pietralikelocals.com/"

def get_page_html():
    response = requests.get(page_link)
    response.raise_for_status()
    page_html = bs4.BeautifulSoup(response.text, "html.parser")

page_html = get_page_html()