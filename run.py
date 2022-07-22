import bs4, requests, validators, json
from tabulate import tabulate

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

        if page_link.startswith("http://") or page_link.startswith("https://"):
            if validate_link(page_link):
                http_url = page_link
                break
        else:
            http_url = add_http(page_link)
            print(f"Added scheme. New url: {http_url}\n")
            if validate_link(http_url):
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

    #This logic check if the url is real by sending a request.
    #If the url is formatted correctly it will go to the next validation.
    try:
        r = requests.get(page_link)
    except:
        print("Url not valid. The program will restart.")
        print("Please enter a real url.\n")
        get_input_url()

    #This validation checks if the url is accessible (if there is a server error)
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
    print("Url is valid...\n")
    print(f"Parsing {http_url} page html...\n")

    response = requests.get(http_url)

    #I used the final url of the redirection chain of response because using the
    #input url would cause errors later.
    final_url = response.url

    print(f"{http_url} redirects to {final_url}...\n")

    #Get html of final_url
    response = requests.get(final_url)
    page_html = bs4.BeautifulSoup(response.text, "html.parser")

    return page_html, response, final_url

def option_selection(final_url,page_html, response, http_url):
    """
    Select an option to start one of the programs.
    """
    option = "0"
    while option != "2" and option != "1" and option != "3" and option != "4":
        print("\nEnter one of the following:\n")
        print("\n1. To get the SEO on page elements.")
        print("2. To get a list of headings with their tags.")
        print("3. To get the page schema markup.")
        print("4. To get all the page links.")

        option = input("Enter one option:\n")

        if option == "2":
            get_headers(page_html)
        if option == "1":
            get_seo_elements(page_html, response, http_url, final_url)
        if option == "3":
            get_page_json(page_html)
        if option == "4":
            get_all_internal_links(page_html)
        else:
            print("\nInvalid entry. Enter a number from 1 to 4.")

def get_seo_elements(page_html, response, http_url, final_url):
    """
    This function finds all the SEO on page elements and builds a dictionary.
    Every SEO element is checked against type None. This is because 
    the rules are set to find the SEO elements only if they exists, 
    are spelled correctly and are lowercase. Without the checks in place, 
    the function will throw multiple errors.
    """

    print("Getting SEO on page elements...\n")

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

    hreflangs = [[a["href"], a["hreflang"]] for a in page_html.find_all("link", href=True, hreflang=True)]

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

    update_on_page_elements(seo_elements)


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

        header_tags = ["Headings not set"]
        header_values = ["Headings not set"]
    
    update_headers(list_headers)


def get_page_json(page_html):
    """
    Get page json and extract schema mark up.
    The error handling skip this step when the schema is not found or invalid or 
    doens't follow the estraction rule.
    """
    print("Parsing the page structured data...\n")
 
    schema_types = []
    schema_headings = []
    
    json_schema = page_html.find("script",attrs={"type":"application/ld+json"})

    if json_schema is None:
        schema_headings = ["There is no structured data."]
    if json_schema is not None:
        json_file = json.loads(json_schema.get_text())

        #In most of the cases a schema dictiorary starts with @graph, 
        #but not always. At this time, I can find the schema @type only if the 
        #dictiorary is @graph.
        try:
            for x in json_file["@graph"]:
                schema_headings.append("@type")
                schema_types.append(x["@type"])            
        except:
            schema_types = None
            pass

    print("Valid structured data...")

    update_schema(schema_types, schema_headings)


def get_all_internal_links(page_html):
    """
    Get all the links on the input webpage. Returns a list of links.
    """
    internal_links = []

    for link in page_html.find_all("a"):
        internal_links.append(link.get("href"))
    
    update_internal_links(internal_links)


def update_on_page_elements(seo_elements):
    """ 
    Receive seo_elements and print the results.
    """
    print(f"Printing on_page_elements...")

    table = zip(seo_elements.keys(), seo_elements.values())
    print(tabulate(table))

    print("on_page_elements printed.\n")

def update_headers(list_headers):
    """ 
    Receive headers and print the results.
    """
    print(f"Printing headers...\n")

    print(tabulate(list_headers))

    print("headers printed.\n")

def update_schema(schema_types, schema_headings):
    """ 
    Receive json schema and print the results.
    """
    print(f"Printing schema types...")

    try:
        if schema_types is not None:
            print(tabulate(schema_types))
            print("schema printed.\n")
        else:
            print("Schema not available.")
    except:
        print("!!!schema worksheet not updated due to invalid schema.!!!\n")
        pass

def update_internal_links(internal_links):
    """ 
    Receive internal_links and print the results.
    """
    print(f"Printing internal_links...")

    for link in internal_links:
        print(link)

    print("internal_links printed.\n")

def final():
    """
    Give a final message to the user. If the user enter 'new' the program restarts
    automatically.
    """
    
    new_crawl = "old"
    while new_crawl != "new":

        new_crawl = input("Enter 'new' to run a new page crawl:\n")

        if new_crawl == "new":
            print("\n")
            main()
        else:
            print("Invalid entry. Enter 'new' to restart.\n")

def main():
    """ 
    Run all the program functions.
    """
    page_link = get_input_url()
    http_url = validate_link(page_link)
    page_html, response, final_url = get_page_html(http_url)
    option_selection(final_url,page_html,response, http_url)    
    final()

main()


	
