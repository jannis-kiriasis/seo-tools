import bs4, requests, gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("seo_tools")

on_page_elements = SHEET.worksheet("on_page_elements")

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
    Return a dictionary of the seo elements parsed.
    """
    print("Parsing the page html...\n")
    response = requests.get(page_link)
    response.raise_for_status()
    page_html = bs4.BeautifulSoup(response.text, "html.parser")

    #Give me title tag, meta description, robots tags and canonical tag
    title = page_html.find("title").get_text()
    meta_description = page_html.find("meta", attrs={"name":"description"})["content"]
    robots = page_html.find("meta", attrs={"name":"robots"})["content"].split(",")
    canonical = page_html.find("link", attrs={"rel":"canonical"})["href"]

    #Give me all the links with href = True and hreflang = True. 
    #This returns all the hreflang
    hreflangs = [[a["href"], a["hreflang"]] 
    for a in page_html.find_all("link", href=True, hreflang=True)]

    h1 = [a.get_text() for a in page_html.find_all('h1')]

    #Give me all the headers in a html document
    headers = page_html.find_all(["h1","h2","h3","h4","h5","h6"])
 
    #Cleaning the headers list to get the tag and the text 
    #as different elements in a list
    list_headers = [[str(x)[1:3], x.get_text()] for x in headers]

    seo_elements = {
        "url": page_link,
        "title": title,
        "meta description": meta_description,
        "robots": robots,
        "canonical": canonical,
        "hreflangs": hreflangs,
        "h1": h1,
        "headers": list_headers
    }

    return seo_elements

def main():
    """ 
    Run all the program functions.
    """
    page_link = get_input_url()
    page_html = get_page_html(page_link)

main()