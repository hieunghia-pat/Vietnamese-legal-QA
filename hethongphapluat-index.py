from bs4 import BeautifulSoup
import requests
import os
import os
import threading
from pdfminer.high_level import extract_text

MAX_PAGE = 43_035
domain = "https://hethongphapluat.com"

def save_pdf(link: str, page, ith) -> None:
    pdf_stream = requests.get(link, stream=True)
    with open(os.path.join("banan-data", f"page_{page}_number_{ith}.pdf"), "wb") as pdf_file:
        pdf_file.write(pdf_stream.content)
    
    text = extract_text(os.path.join("banan-data", f"page_{page}_number_{ith}.pdf"))
    with open(os.path.join("banan-data", f"page_{page}_number_{ith}.txt"), "w+") as text_file:
            text_file.write(text)

    os.remove(os.path.join("banan-data", f"page_{page}_number_{ith}.pdf"))

def start_crawling_page(page_id):
    url = os.path.join(domain, f"thu-vien-ban-an_page-{page_id}.html")
    while True:
        try:
            main_content = requests.get(url).content
            break
        except:
            continue
    main_soup = BeautifulSoup(main_content, features="lxml")

    print("Start parsing ", url)

    for ith, div in enumerate(main_soup.find_all('div', class_="list-body"), start=1):
        link = div.a["href"]
        thread = threading.Thread(
            target=start_crawling_pdf,
            args=(link, page, ith, )
        )
        thread.start()

def start_crawling_pdf(link, page, ith):
    link = os.path.join(domain, link)
    print("Start collecting pdf file in ", link)
    session = requests.Session()   
    while True:
        try:
            content = session.get(link).content
            break
        except:
            continue
    soup = BeautifulSoup(content, features="lxml")

    while True:
        try:
            al_content = soup.find("div", {"id": "al_content"})
            link_to_pdf = al_content.object["data"]
            if link_to_pdf == "":
                print("There is no pdf file available in", link)
                return
            save_pdf(link_to_pdf, page, ith)
            break
        except:
            continue

    print("Collected pdf file in ", link)

if __name__ == "__main__":
    for page in range(1, 2):
        start_crawling_page(page)
