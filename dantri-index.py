from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--domain", type=str, required=True)
parser.add_argument("--max-page", type=int, default=30)

args = parser.parse_args()

parsed_links = []
main_url = f'https://dantri.com.vn/{args.domain}'

data = {
    "articles": [],
    "source": "vnexpress",
    "domain": args.domain
}

for page in range(1, args.max_page+1):
    url = main_url + f"/trang-{page}.htm"
    main_soup = BeautifulSoup(requests.get(url).content, features="lxml")
    session = requests.Session()

    print(url)

    with tqdm(main_soup.find_all("div", class_="article-content")) as pb:
        for div in pb:
            title = div.h3.a.text
            link = div.h3.a["href"]
            link = f"{main_url}{link}"

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

            div = soup.find('div', class_="singular-content")
            if div is None:
                div = soup.find('div', class_="e-magazine__body")

            if div is None:
                continue

            for p in div.find_all("p"):
                if p.string is None:
                    continue
                article["passages"].append(p.string)
                
            data["articles"].append(article)

            parsed_links.append(link)

print("Saving ...")
json.dump(data, open(f"dantri.json", "w+"), ensure_ascii=False, indent=4)