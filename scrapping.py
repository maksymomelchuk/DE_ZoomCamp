import requests
from bs4 import BeautifulSoup

def get_data(url):
    headers = {
        "user-agent" : 
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"
    }
    req = requests.get(url, headers)
    print(req.text)

    with open("projects.html", "w") as file:
        file.write(req.text)

get_data("https://scholar.google.com/citations?view_op=view_org&hl=en&org=3918598370877205258")