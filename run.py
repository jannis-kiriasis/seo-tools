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
    """
    Select an option to start one of the 2 programs.
    """
    option = 0
    while option != "2" and option != "1":
        print("\nEnter one of the following:\n")
        print("\n1 to enter a URL and get a list of the pages within that subdomain.")
        print("2 to enter a URL and get its SEO on page elements.\n")

        option = input("Enter 1 or 2:\n")

        if option == "2":
            main()
        if option == "1":
            site_urls()
        else:
            print("Invalid entry. Enter 1 or 2.")

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
    """
    This function finds all the SEO on page elements and builds a dictionary.
    Every SEO element is checked against type None. This is because 
    the rules are set to find the SEO elements only if they exists, 
    are spelled correctly and are lowercase. Without the checks in place, 
    the function will throw multiple errors.
    """

    print("Getting SEO on page elements...\n")

    #If the input url redirects to a new url, the following loop gives a list
    #of all the redirects until the final url 

    for r in response.history:
        final_url = response.url

    #check if the title tag isn't None with the find method
    title_temp = page_html.find("title")

    if title_temp is None:
        title = "not available"
    if title_temp is not None:
        title = title_temp.get_text()

    #check if the meta description isn't None with the find method

    meta_desc_temp = page_html.find("meta", attrs={"name":"description"})
    
    if meta_desc_temp is None:
        meta_description = "not available"
    if meta_desc_temp is not None:
        meta_description = meta_desc_temp["content"]

    #check if robots aren't None with the find method

    robots_temp = page_html.find("meta", attrs={"name":"robots"})

    if robots_temp is None:
        robots = "Not available"
    if robots_temp is not None:
        robots = robots_temp["content"]
    
    #check if rel=canonical isn't None with the find method

    canonical_temp = page_html.find("link", attrs={"rel":"canonical"})
    
    if canonical_temp is None:
        canonical = "Not available"
    if canonical_temp is not None:
        canonical = canonical_temp["href"]   

    #Give me all the links with href = True and hreflang = True. 
    #This returns all the hreflang

    hreflangs = [[a['href'], a["hreflang"]] for a in page_html.find_all('link', href=True, hreflang=True)]

    #To display hreflangs in 1 cell in the worksheet
    hreflangs_str = str(",".join(str(x) for x in hreflangs))

    if hreflangs_str == "":
        hreflangs_str = "Not set"

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

def get_headers(page_html, seo_elements):
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
    #The while loop takes all the elements in position 0 and create a list.
    #Then all the elements in position 1 and create a list.
    i = 0    
    header_tags = []
    header_values = []

    while i < len(list_headers):
        header_tags.append(list_headers[i][0])
        header_values.append(list_headers[i][1])
        i += 1
    
    #If the headings don't exist, write "URL headings not set" instead of 
    #leaving a black worksheet

    if header_tags == [] and header_values == []:

        header_tags = ["'" + seo_elements["final url"] + "'" + " headings not set"]
        header_values = ["'" + seo_elements["final url"] + "'" + " headings not set"]
    
    return header_tags, header_values

def get_page_json(page_html):
    """
    Get page json and extract schema mark up.
    The error handling skip this step when the schema is not found or invalid or 
    doens't follow the estraction rule.
    """
    print("Parsing the page structured data...\n")
 
    schema_types = []
    schema_headings = []
    
    json_schema = page_html.find('script',attrs={'type':'application/ld+json'})

    if json_schema is None:
        schema_headings = ["There is no structured data."]
    if json_schema is not None:
        json_file = json.loads(json_schema.get_text())
        try:
            for x in json_file["@graph"]:
                schema_headings.append("@type")
                schema_types.append(x["@type"])            
        except:
            schema_types = ["Schema structured data not available. @graph not found"]
            pass

    return schema_types, schema_headings

    print("Valid structured data...")

def get_all_internal_links(page_html, response, seo_elements):
    """
    Get all the links on the input webpage. Returns a list of links.
    """
    internal_links = []

    for link in page_html.find_all("a"):
        internal_links.append(link.get("href"))
    
    print(internal_links)

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

    try:
        schema.append_row(schema_headings)
        schema.append_row(schema_types)
        print("schema worksheet updated.\n")
    except:
        print("!!!schema worksheet not updated due to invalid schema.!!!\n")
        pass

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
    header_tags, header_values = get_headers(page_html, seo_elements)
    schema_types, schema_headings = get_page_json(page_html)
    internal_links = get_all_internal_links(page_html, response, seo_elements)
    update_on_page_elements_worksheet(seo_elements)
    update_headers_worksheet(header_tags, header_values)
    update_schema_worksheet(schema_types, schema_headings)
    #update_internal_links_worksheet(internal_links)

main()
#option_selection()

def site_urls():
    site="https://pietralikelocals.com"
    scrape(site)

