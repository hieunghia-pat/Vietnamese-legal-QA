import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import threading
import re
import os

BASE_DIR = "thuvienphapluat-links"

def parsing_content(link, name):
    session = requests.Session()
    while True:
        try:
            content = session.get(link).content
            break
        except:
            print(f"Retrying for {link}")
            continue

    soup = BeautifulSoup(content, 'html.parser')
    div = soup.find("div", {"class": "content1"})
    passages = []
    with tqdm(div.find_all("p"), desc=f"Getting {name}") as ps:
        for p in ps:
            passages.append(p.text)

    passage = "\n\n".join(passages)
    name = re.sub("/", "", name)
    with open(os.path.join("data", f"{name}.json"), "w+") as file:
        file.write(passage)

if __name__ == "__main__":
    txt_files = os.listdir(BASE_DIR)
    links = []
    for txt_file in txt_files:
        with open(os.path.join(BASE_DIR, txt_file)) as file:
            links.extend(file.readlines())

    total_threats = len(links) // 10
    current_threads = []
    for ith in range(total_threats):
        for link in links[ith*total_threats: (ith+1)*total_threats]:
            name = link.split("/")[-1]
            name = re.sub(".aspx", "", name)
            name = re.sub("/", "-". name)
            thread = threading.Thread(
                target=parsing_content,
                args=(link, name)
            )
            thread.start()
            current_threads.append(thread)
            if len(current_threads) == 10:
                for thread in current_threads:
                    thread.join()
                current_threads = []

    print("Done")