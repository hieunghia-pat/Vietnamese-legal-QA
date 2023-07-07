from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import json

MAX_PAGE = 40
parsed_link = set()
domain = "https://hethongphapluat.com/thu-tuc-hanh-chinh"
for page in range(MAX_PAGE):
    url = f"{domain}_page-{page}.html"
    
    main_soup = BeautifulSoup(requests.get(url).content, features="lxml")
    session = requests.Session()

    print(url)
    
    with tqdm(main_soup.find_all("div", class_="list-body")) as pb:
        for div in pb:
            link = div.find("a")["href"]
            title = div.find("a")["title"]
            
            pb.set_postfix_str(f"Parsing \"{title}\"")

            if link in parsed_link:
                continue
            
            parsed_link.add(link)

            content = session.get(link).content
            soup = BeautifulSoup(content, features="lxml")
            
