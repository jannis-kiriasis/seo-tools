import bs4, requests, gspread, validators
from google.oauth2.service_account import Credentials
import json

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
headers_worksheet = SHEET.worksheet("headers")
schema = SHEET.worksheet("schema")
internal_links_worksheet = SHEET.worksheet("internal_links")

def option_selection():
    option = 0
    while option != "2":
        print("\nEnter one of the following:\n")
        print("\n1 to enter a URL and get a list of the pages within that subdomain.\n")
        print("\n2 to enter a URL and get its SEO on page elements.\n")

        option = input("Enter 1 or 2:\n")

        if option == "2":
            main()
        else:
            print("Invalid entry. Enter 1 or 2")


internal_links = []

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
    print(f"Parsing {http_url} page html...\n")
    response = requests.get(http_url)
    page_html = bs4.BeautifulSoup(response.text, "html.parser")
    return page_html, response

def get_seo_elements(page_html, response, http_url):
    #If the input url redirects to a new url, the following loop gives a list
    #of all the redirects until the final url 
    for r in response.history:
        final_url = response.url

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

    seo_elements = {
        "input url": http_url,
        "final url": final_url,
        "title": title,
        "title_length": str(len(title)) + "/ 65",
        "meta_description": meta_description,
        "meta_description_length": str(len(meta_description)) + "/ 154",
        "robots": robots,
        "canonical": canonical,
        "hreflangs": hreflangs_str,
    }

    return seo_elements

def get_headers(page_html):
    """
    Get the headers from the page html.
    Create a list of header tags and a list of header tag values.
    """
    #Give me all the headers in a html document
    headers = page_html.find_all(["h1","h2","h3","h4","h5","h6"])
 
    #Cleaning the headers list to get the tag and the text 
    #as different elements in a list
    list_headers = [[str(x)[1:3], x.get_text()] for x in headers]

    #Separate the header tags and tag values in 2 different lists
    i = 0    
    header_tags = []
    header_values = []

    while i < len(list_headers):
        header_tags.append(list_headers[i][0])
        header_values.append(list_headers[i][1])
        i += 1
    
    return header_tags, header_values

def get_page_json(page_html):
    json_schema = page_html.find('script',attrs={'type':'application/ld+json'})
    json_file = json.loads(json_schema.get_text())

    schema_types = []
    schema_headings = []

    for x in json_file["@graph"]:
        schema_types.append(x["@type"])
        schema_headings.append("@type")
    return schema_types, schema_headings

def get_all_internal_links(page_html, response, seo_elements):

    url = seo_elements["final url"]

    for link in page_html.find_all("a"):
        
        internal_links.append(link.get("href"))

    return internal_links

def update_on_page_elements_worksheet(seo_elements):
    """ 
    Receive seo_elements to be inserted in a worksheet.
    Update the worksheet with the data provided.
    """
    print(f"Updating on_page_elements worksheet...")

    on_page_elements.append_row(list(seo_elements.keys()))
    on_page_elements.append_row(list(seo_elements.values()))

    print("on_page_elements worksheet updated.\n")

def update_headers_worksheet(header_tags, header_values):
    """ 
    Receive headers to be inserted in a worksheet.
    Update the worksheet with the data provided.
    """
    print(f"Updating headers worksheet...")

    headers_worksheet.append_row(header_tags)
    headers_worksheet.append_row(header_values)

    print("headers worksheet updated.\n")

def update_schema_worksheet(schema_types, schema_headings):
    """ 
    Receive json schema to be inserted in a worksheet.
    Update the worksheet with the data provided.
    """
    print(f"Updating schema worksheet...")

    schema.append_row(schema_headings)
    schema.append_row(schema_types)

    print("schema worksheet updated.\n")

def update_internal_links_worksheet(internal_links):
    """ 
    Receive internal_links to be inserted in a worksheet.
    Update the worksheet with the data provided.
    """
    print(f"Updating internal_links worksheet...")

    internal_links_worksheet.append_row(internal_links)

    print("internal_links worksheet updated.\n")

def main():
    """ 
    Run all the program functions.
    """
    page_link = get_input_url()
    http_url = validate_link(page_link)
    page_html, response = get_page_html(http_url)
    seo_elements = get_seo_elements(page_html, response, http_url)
    header_tags, header_values = get_headers(page_html)
    schema_types, schema_headings = get_page_json(page_html)
    internal_links = get_all_internal_links(page_html, response, seo_elements)
    update_on_page_elements_worksheet(seo_elements)
    update_headers_worksheet(header_tags, header_values)
    update_schema_worksheet(schema_types, schema_headings)
    update_internal_links_worksheet(internal_links)

option_selection()