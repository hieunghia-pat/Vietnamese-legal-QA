import re
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import json
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--domain", required=False, type=str, default="")
parser.add_argument("--topic", required=True, type=str)
args = parser.parse_args()

parsed_links = []
domain = args.domain
topic = args.topic

if domain != "":
    topic = f"{domain}/{topic}"

main_url = f'https://vietnamnet.vn/{topic}'

data = {
    "articles": [],
    "source": "vietnamnet",
    "domain": domain
}

for page in range(43):
    url = main_url + f"-page{page}"
    main_soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    session = requests.Session()

    print(url)

    with tqdm(main_soup.find_all('div')) as pb:
        for div in pb:
            if not div.has_attr("class"):
                continue

            if not ("verticalPost" in div["class"] or "horizontalPost" in div["class"]):
                continue

            a = div.div.a

            title = a["title"]
            link = a['href']
            link = re.sub("https://vietnamnet.vn", "", link)
            link = f"https://vietnamnet.vn{link}"

            pb.set_postfix_str(f"Parsing \"{title}\"")

            if link in parsed_links:
                continue

            try:
                content = session.get(link).content
            except Exception as error:
                print(f"Error while retrieving from {link}")
                continue

            soup = BeautifulSoup(content, 'html.parser')

            article = {
                "link": link,
                "title": title,
                "passages": []
            }

            main_content = None
            for div in soup.find_all("div"):
                if "class" in div.attrs and "maincontent" in div["class"]:
                    main_content = div
                    break

            if main_content is None:
                continue

            for tag in main_content.find_all('p'):
                if "class" in tag.attrs and "article-relate" in tag:
                    continue
                passage = tag.text
                article["passages"].append(passage)
                
            data["articles"].append(article)

            parsed_links.append(link)

json.dump(data, open(f"vietnamnet_{domain}.json", "w+"), ensure_ascii=False)