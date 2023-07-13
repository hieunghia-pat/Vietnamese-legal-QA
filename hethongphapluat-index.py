from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import os
import json
import os
import re
import argparse
import docx
import threading
import multiprocessing

parser = argparse.ArgumentParser()
parser.add_argument("--from-page", type=int, required=True)
parser.add_argument("--to-page", type=int, required=True)
args = parser.parse_args()

MAX_PAGE = 43_035
FROM_PAGE = args.from_page
TO_PAGE = args.to_page
domain = "https://hethongphapluat.com"

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

def start_crawling_page(page_id):
    url = os.path.join(domain, f"thu-vien-ban-an_page-{page_id}.html")
    
    main_soup = BeautifulSoup(requests.get(url).content, features="lxml")

    print("Start parsing ", url)

    threads = []
    for div in main_soup.find_all('div', class_="list-body"):
        link = div.a["href"]
        thread = threading.Thread(
            target=start_crawling_docx,
            args=(link, )
        )
        thread.start()
        threads.append(thread)

    print("Parsed ", url)

def start_crawling_docx(link):
    print("Start collecting docx file in ", link)
    session = requests.Session()   
    while True:
        try:
            content = session.get(link).content
            break
        except:
            continue
    soup = BeautifulSoup(content, features="lxml")

    try:
        download_section = soup.find("div", {"class": "download-section"})
        button = download_section.find_all("button")[1]
    except:
        print("Cannot find download section for ", link)
        return

    link_to_docx = button.a["href"]
    if link_to_docx == "":
        print("There is not docx file available ")
        return

    while True:
        try:
            ba_info = soup.find("div", {"class": "ba-info"})
            li = ba_info.ul.find_all("li")[0]
            li_text = li.text
            li_text = re.sub("Số bản án:", "", li_text).strip()
            save_docx(link_to_docx, li_text)
            break
        except:
            continue

    print("Collected docx file in ", link)

processes = []
for page in range(FROM_PAGE, TO_PAGE):
    process = multiprocessing.Process(
        target=start_crawling_page, 
        args=(page, )
    )
    process.start()
    processes.append(process)

for process in processes:
    process.join()

print("Done")

if __name__ == "__main__":
    pass