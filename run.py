import bs4, requests, gspread, validators
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
    Check if the url starts with http, if not add http scheme.
    After check for http, check if url works.
    Return url with http.
    """
    while True:
        print("Are you ready to scrape a webpage?")
        page_link = input("Enter the url you want to scrape:\n")

        print(f"Thank you! I'm validating {page_link}...\n")
        print("Checking http schema...\n")

        if page_link.startswith("http://" and "https://"):
            if validate_link(page_link):
                print("Url is valid!")
                http_url = page_link
                break
        else:
            http_url = add_http(page_link)
            print(f"Added scheme. New url: {http_url}\n")
            if validate_link(http_url):
                print("Url is valid!")
                break

    return http_url

    http_url = page_link
    return http_url

def add_http(page_link):
    """ 
    This function adds the http scheme in front of the url in case it is missing.
    Then after the http as been added, the url is passed to validate_link.
    """
    page_link = "http://" + page_link
    return page_link

def validate_link(page_link):
    """ 
    Check if the user input is a valid url.
    """
    valid = validators.url(page_link)
    if valid == True:
        http_url = page_link
        return http_url
    else:
        print("Invalid url...")
        print("Please enter a valid url.\n")
        return False

def get_page_html(http_url):
    """
    Send a get HTTP request to page_link and receive the html of the page.
    raise_for_status verifies that the request is good.
    Return a dictionary of the seo elements parsed.
    """
    print("Parsing the page html...\n")
    response = requests.get(http_url)
    response.raise_for_status()
    page_html = bs4.BeautifulSoup(response.text, "html.parser")

    #Give me title tag, meta description, robots tags and canonical tag
    title = page_html.find("title").get_text()
    meta_description = page_html.find("meta", attrs={"name":"description"})["content"]
    robots = page_html.find("meta", attrs={"name":"robots"})["content"]
    canonical = page_html.find("link", attrs={"rel":"canonical"})["href"]

    #Give me all the links with href = True and hreflang = True. 
    #This returns all the hreflang
    hreflangs = [[a["href"], a["hreflang"]] 
    for a in page_html.find_all("link", href=True, hreflang=True)]

    #To display hreflangs in 1 cell in the worksheet
    hreflangs_str = str(",".join(str(x) for x in hreflangs))

    h1 = [a.get_text() for a in page_html.find_all('h1')]

    #To display h1s in 1 cell in the worksheet
    h1_str = str(",".join(str(x) for x in h1))

    #Give me all the headers in a html document
    headers = page_html.find_all(["h1","h2","h3","h4","h5","h6"])
 
    #Cleaning the headers list to get the tag and the text 
    #as different elements in a list
    list_headers = [[str(x)[1:3], x.get_text()] for x in headers]

    #To display headers in 1 cell in the worksheet
    headers_str = str(",".join(str(x) for x in list_headers))

    seo_elements = {
        "url": http_url,
        "title": title,
        "meta description": meta_description,
        "robots": robots,
        "canonical": canonical,
        "hreflangs": hreflangs_str,
        "h1": h1_str,
        "headers": headers_str
    }

    return seo_elements

def update_seo_tools_worksheet(seo_elements):
    """ 
    Receive a dictionary to be inserted in a worksheet.
    Update the worksheet with the data provided.
    """
    print(f"Updating on_page_elements worksheet...\n")

    on_page_elements.append_row(list(seo_elements.keys()))
    on_page_elements.append_row(list(seo_elements.values()))

    print("Worksheet updated.")

def main():
    """ 
    Run all the program functions.
    """
    page_link = get_input_url()
    http_url = validate_link(page_link)
    seo_elements = get_page_html(http_url)
    update_seo_tools_worksheet(seo_elements)

main()