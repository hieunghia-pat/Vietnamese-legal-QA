from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import os
import json
import os
import re
import argparse
import docx

parser = argparse.ArgumentParser()
parser.add_argument("--from-page", type=int, required=True)
parser.add_argument("--to-page", type=int, required=True)
args = parser.parse_args()

MAX_PAGE = 43_035
FROM_PAGE = args.from_page
TO_PAGE = args.to_page
domain = "https://hethongphapluat.com"
parsed_link = set()
data = []

def parsing_docx_file(link: str) -> list:
    docx_stream = requests.get(link, stream=True)
    with open("file.docx", "wb") as docx_file:
        docx_file.write(docx_stream.content)

    doc = docx.Document("file.docx")
    paragraphs = []
    for paragraph in doc.paragraphs:
        if len(paragraph.text.split()) > 0:
            paragraphs.append(paragraph.text)

    return paragraphs

def save_docx(link: str, docx_id: str) -> None:
    docx_id = re.sub("/", "-", docx_id)
    docx_stream = requests.get(link, stream=True)
    with open(os.path.join("data", f"{docx_id}.docx"), "wb") as docx_file:
        docx_file.write(docx_stream.content)

for page in range(FROM_PAGE, TO_PAGE):
    url = os.path.join(domain, f"thu-vien-ban-an_page-{page}.html")
    
    main_soup = BeautifulSoup(requests.get(url).content, features="lxml")
    while True:
        try:
            session = requests.Session()
            break
        except:
            continue

    print(url)

    for div in main_soup.find_all('div', class_="list-body"):
        link = div.a["href"]
        title = div.a["title"]

        title = " ".join(title.split()[:5])
        
        if link in parsed_link:
            continue

        link = os.path.join(domain, link)
        while True:
            try:
                content = session.get(link).content
                break
            except:
                continue
        soup = BeautifulSoup(content, features="lxml")

        item = {}

        try:
            download_section = soup.find("div", {"class": "download-section"})
            button = download_section.find_all("button")[1]
        except:
            print("Cannot find download section for ", link)
            continue

        link_to_docx = button.a["href"]
        if link_to_docx == "":
            continue
        # paragraphs = parsing_docx_file(link_to_docx)
        # item["paragraphs"] = paragraphs
        
        right_ba_info = soup.find("div", {"id": "right-ba-info"})
        item["info"] = right_ba_info.h1.text

        ba_info = soup.find("div", {"class": "ba-info"})
        li = ba_info.ul.find_all("li")[0]
        li_text = li.text
        li_text = re.sub("Số bản án:", "", li_text).strip()
        item["number"] = li_text
        save_docx(link_to_docx, li_text)

        data.append(item)

json.dump(data, open(f"hethongphapluat-banan_from-{FROM_PAGE}_to-{TO_PAGE}.json", "w+"), ensure_ascii=False, indent=4)
print("Done")