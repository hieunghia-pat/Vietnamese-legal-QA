import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import threading
import re
import os

def parsing_content(link, id, name):
    print(f"Getting {name}")
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
    with tqdm(div.find_all("p")) as ps:
        for p in ps:
            passages.append(p.text)

    passage = "\n\n".join(passages)
    name = re.sub("/", "", name)
    json.dump({
        "id": id,
        "link": link,
        "passage": passage
    }, open(os.path.join("data", f"data_{id}_{name}.json"), "w+"), ensure_ascii=False, indent=4)

if __name__ == "__main__":
    data = json.load(open("DataForDemo.json"))

    current_threads = []
    for key in data:
        item = data[key]
        link_item = item["href"]
        for law_name in link_item:
            link = link_item[law_name]
            thread = threading.Thread(
                target=parsing_content,
                args=(link, key, law_name, )
            )
            thread.start()
            current_threads.append(thread)
            if len(current_threads) == 10:
                for thread in current_threads:
                    thread.join()
                current_threads = []

    print("Done")