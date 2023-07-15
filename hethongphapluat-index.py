from bs4 import BeautifulSoup
import requests
import os
import os
import re
import threading

MAX_PAGE = 43_035
domain = "https://hethongphapluat.com"
id = 0

def save_pdf(link: str, pdf_id: str) -> None:
    pdf_id = re.sub("/", "-", pdf_id)
    pdf_stream = requests.get(link, stream=True)
    global id
    id += 1
    with open(os.path.join("banan-data", f"{id}.pdf"), "wb") as pdf_file:
        pdf_file.write(pdf_stream.content)

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

    threads = []
    for div in main_soup.find_all('div', class_="list-body"):
        link = div.a["href"]
        thread = threading.Thread(
            target=start_crawling_pdf,
            args=(link, )
        )
        thread.start()
        threads.append(thread)

def start_crawling_pdf(link):
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
            ba_info = soup.find("div", {"class": "ba-info"})
            li = ba_info.ul.find_all("li")[0]
            li_text = li.text
            li_text = re.sub("Số bản án:", "", li_text).strip()
            save_pdf(link_to_pdf, li_text)
            break
        except:
            continue

    print("Collected pdf file in ", link)

if __name__ == "__main__":
    for page in range(1, MAX_PAGE+1):
        start_crawling_page(page)

    print("Done")
