import re
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--domain", type=str, required=True)
parser.add_argument("--topic", type=str, required=True)
parser.add_argument("--max-page", type=int, required=True)

args = parser.parse_args()

parsed_links = []
main_url = f'https://vnexpress.net/{args.domain}/{args.topic}'

data = {
    "articles": [],
    "source": "vnexpress",
    "domain": args.domain,
    "tag": args.topic
}

for page in range(1, args.max_page):
    url = main_url + f"-p{page}"
    main_soup = BeautifulSoup(requests.get(url).content, features="lxml")
    session = requests.Session()

    print(url)

    with tqdm(main_soup.find_all('article')) as pb:
        for article in pb:
            if article.p is None:
                continue

            title = article.p.a["title"] if "title" in article.p.a else article.p.a.text
            link = article.p.a["href"]

            pb.set_postfix_str(f"Parsing \"{title}\"")

            if link in parsed_links:
                continue

            content = session.get(link).content
            soup = BeautifulSoup(content, features="lxml")

            article = {
                "link": link,
                "title": title,
                "passages": []
            }

            for tag in soup.find_all('p'):
                if 'class' in tag.attrs and 'Normal' in tag['class']:
                    if tag.string:
                        article["passages"].append(tag.string)
                
            data["articles"].append(article)

            parsed_links.append(link)

json.dump(data, open(f"vnexpress_{args.domain}_{args.topic}.json", "w+"), ensure_ascii=False)